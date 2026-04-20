import io


def test_upload_indexes_chunks(client, monkeypatch, dummy_runtime):
    import app.api.routes.upload as upload_route

    stored = {"called": False, "chunks": 0}

    monkeypatch.setattr(
        upload_route,
        "extract_pages_from_pdf",
        lambda _: [{"page_number": 1, "text": "Alice signed the lease on 2025-07-09."}],
    )
    monkeypatch.setattr(upload_route, "get_runtime_providers", lambda: dummy_runtime)
    monkeypatch.setattr(upload_route, "reset_collection", lambda: None)

    def _fake_store_chunks(chunks, source_file, embedding_provider):
        del source_file
        del embedding_provider
        stored["called"] = True
        stored["chunks"] = len(chunks)

    monkeypatch.setattr(upload_route, "store_chunks", _fake_store_chunks)

    files = {"file": ("lease.pdf", io.BytesIO(b"%PDF-test"), "application/pdf")}
    response = client.post("/upload/", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["chunk_count"] >= 1
    assert stored["called"] is True
    assert stored["chunks"] >= 1


def test_upload_rejects_non_pdf(client):
    files = {"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")}
    response = client.post("/upload/", files=files)
    assert response.status_code == 400
