import time

import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Document Assistant", layout="wide")
st.title("AI Document Assistant")
st.caption("Upload a PDF, index it, and ask grounded questions.")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("Backend")
    backend_url = st.text_input("FastAPI URL", value=BACKEND_URL)
    top_k = st.slider("Top-K retrieval", min_value=1, max_value=20, value=10)
    st.markdown("### Run history")
    if not st.session_state.history:
        st.write("No runs yet.")
    else:
        for item in reversed(st.session_state.history[-10:]):
            st.markdown(
                f"- `{item['mode']}` | {item['latency_ms']}ms | "
                f"{item['match_count']} matches | {item['question']}"
            )

st.subheader("1. Upload PDF")
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None and st.button("Upload and Index"):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    with st.spinner("Uploading and indexing document..."):
        response = requests.post(f"{backend_url}/upload/", files=files, timeout=300)

    if response.ok:
        data = response.json()
        st.success(data["message"])
        st.json(
            {
                "filename": data["filename"],
                "text_length": data["text_length"],
                "page_count": data["page_count"],
                "chunk_count": data["chunk_count"],
                "preview": data["preview"],
            }
        )
    else:
        st.error(response.text)

st.subheader("2. Ask a Question")
question = st.text_input("Ask something about the document")

if st.button("Get Answer"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        started = time.perf_counter()
        with st.spinner("Retrieving answer..."):
            response = requests.post(
                f"{backend_url}/query/",
                json={"question": question, "top_k": int(top_k)},
                timeout=300,
            )
        ui_latency = int((time.perf_counter() - started) * 1000)

        if response.ok:
            result = response.json()
            st.markdown("### Answer")
            st.write(result["answer"])

            st.info(
                f"Mode: {result['runtime_mode']} | API latency: {result['latency_ms']}ms | "
                f"UI total latency: {ui_latency}ms | Matches: {result['match_count']}"
            )

            st.markdown("### Sources")
            for source in result["sources"]:
                with st.expander(
                    f"{source['source_file']} | page {source['page_number']} | "
                    f"chunk {source['chunk_index']} | distance {source['distance']} | "
                    f"confidence {source['confidence']}"
                ):
                    st.write(source["text_preview"])

            st.session_state.history.append(
                {
                    "question": question,
                    "answer": result["answer"][:120],
                    "latency_ms": result["latency_ms"],
                    "mode": result["runtime_mode"],
                    "match_count": result["match_count"],
                }
            )
        else:
            st.error(response.text)
