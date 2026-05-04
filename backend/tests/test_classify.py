import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_classify_technical():
    resp = client.post("/classify", json={"text": "The API endpoint is returning a database error in the server code"})
    assert resp.status_code == 200
    assert resp.json()["category"] == "technical"


def test_classify_business():
    resp = client.post("/classify", json={"text": "Our Q3 revenue strategy meeting with the client will review KPI roadmap"})
    assert resp.status_code == 200
    assert resp.json()["category"] == "business"


def test_classify_casual():
    resp = client.post("/classify", json={"text": "Hey! Sounds good, let's catch up for lunch this weekend, lol"})
    assert resp.status_code == 200
    assert resp.json()["category"] == "casual"


def test_classify_other():
    resp = client.post("/classify", json={"text": "The quick brown fox jumps over the lazy dog"})
    assert resp.status_code == 200
    assert resp.json()["category"] == "other"


def test_classify_empty_string():
    resp = client.post("/classify", json={"text": ""})
    assert resp.status_code == 422


def test_classify_whitespace_only():
    resp = client.post("/classify", json={"text": "   "})
    assert resp.status_code == 422


def test_classify_too_long():
    resp = client.post("/classify", json={"text": "a" * 1001})
    assert resp.status_code == 422


def test_classify_missing_text_field():
    resp = client.post("/classify", json={})
    assert resp.status_code == 422


def test_classify_confidence_range():
    resp = client.post("/classify", json={"text": "fix the bug in the API endpoint code"})
    assert resp.status_code == 200
    data = resp.json()
    assert 0.0 <= data["confidence"] <= 1.0
