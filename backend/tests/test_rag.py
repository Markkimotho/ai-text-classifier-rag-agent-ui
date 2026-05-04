import io
import sys
import os

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import rag as rag_module
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rag_store():
    rag_module.reset_store()
    yield
    rag_module.reset_store()


TXT_CONTENT = b"""
FastAPI is a modern, fast web framework for building APIs with Python.
It is based on standard Python type hints and uses Pydantic for data validation.
FastAPI automatically generates OpenAPI documentation for all endpoints.
The framework is built on top of Starlette and supports async request handling.
Developers love FastAPI because of its speed and ease of use.
"""


def _make_txt_file(content: bytes = TXT_CONTENT, filename: str = "test.txt"):
    return ("file", (filename, io.BytesIO(content), "text/plain"))


def test_upload_txt():
    resp = client.post("/upload", files=[_make_txt_file()])
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test.txt"
    assert data["chunks_stored"] > 0


def test_upload_unsupported_type():
    resp = client.post(
        "/upload",
        files=[("file", ("doc.docx", io.BytesIO(b"data"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
    )
    assert resp.status_code == 400


def test_ask_after_upload():
    client.post("/upload", files=[_make_txt_file()])
    resp = client.post("/ask", json={"question": "What is FastAPI?"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["answer"], str) and len(data["answer"]) > 0
    assert isinstance(data["sources"], list) and len(data["sources"]) > 0


def test_documents_list():
    client.post("/upload", files=[_make_txt_file()])
    resp = client.get("/documents")
    assert resp.status_code == 200
    docs = resp.json()["documents"]
    assert "test.txt" in docs


def test_documents_empty_initially():
    resp = client.get("/documents")
    assert resp.status_code == 200
    assert resp.json()["documents"] == []


def test_ask_no_documents_returns_answer():
    resp = client.post("/ask", json={"question": "What is the meaning of life?"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["answer"], str)
