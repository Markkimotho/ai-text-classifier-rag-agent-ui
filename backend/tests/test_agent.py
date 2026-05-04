import io
import sys
import os

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import rag as rag_module
from agent import reset_memory
from main import app

client = TestClient(app)

TXT_CONTENT = b"""
FastAPI is a modern Python web framework for building APIs.
It uses Pydantic for validation and supports async operations.
The framework auto-generates OpenAPI documentation.
LangChain is an orchestration framework for LLM-powered applications.
"""


@pytest.fixture(autouse=True)
def reset_state():
    rag_module.reset_store()
    reset_memory()
    yield
    rag_module.reset_store()
    reset_memory()


def test_ask_calculator():
    resp = client.post("/ask", json={"question": "What is 144 / 12?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Calculator" in data["tool_trace"]
    assert "12" in data["answer"]


def test_ask_current_time():
    resp = client.post("/ask", json={"question": "What time is it right now?"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Current Time" in data["tool_trace"]


def test_ask_document_question_after_upload():
    client.post(
        "/upload",
        files=[("file", ("doc.txt", io.BytesIO(TXT_CONTENT), "text/plain"))],
    )
    resp = client.post("/ask", json={"question": "What does the document say about FastAPI?"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["sources"], list) and len(data["sources"]) > 0


def test_ask_response_schema():
    resp = client.post("/ask", json={"question": "Hello!"})
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "tool_trace" in data
    assert "sources" in data
    assert isinstance(data["tool_trace"], list)
    assert isinstance(data["sources"], list)


def test_ask_multi_turn_memory():
    client.post("/ask", json={"question": "My favourite framework is FastAPI."})
    resp = client.post("/ask", json={"question": "What framework did I just mention?"})
    assert resp.status_code == 200
    # The second response should reference FastAPI (it's in the conversation history)
    data = resp.json()
    assert isinstance(data["answer"], str) and len(data["answer"]) > 0
