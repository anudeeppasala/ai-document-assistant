def test_query_returns_answer_and_sources(client, monkeypatch):
    import app.api.routes.query as query_route

    monkeypatch.setattr(
        query_route,
        "retrieve_relevant_chunks",
        lambda question, top_k=None: [
            {
                "source_file": "lease.pdf",
                "chunk_index": 3,
                "page_number": 2,
                "distance": 0.21,
                "text": "Tenant: Alice Johnson",
            }
        ],
    )
    monkeypatch.setattr(
        query_route,
        "generate_answer_from_chunks",
        lambda question, matches: f"Tenant is Alice Johnson ({len(matches)} hits)",
    )
    monkeypatch.setattr(query_route, "get_runtime_mode", lambda: "OFFLINE")

    response = client.post("/query/", json={"question": "Who is the tenant?"})
    assert response.status_code == 200
    body = response.json()
    assert body["match_count"] == 1
    assert body["runtime_mode"] == "OFFLINE"
    assert "Alice" in body["answer"]
    assert body["sources"][0]["page_number"] == 2


def test_query_rejects_empty_question(client):
    response = client.post("/query/", json={"question": "   "})
    assert response.status_code == 400
