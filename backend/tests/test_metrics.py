import sys
import os

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


def test_metrics_endpoint_returns_200():
    resp = client.get("/metrics")
    assert resp.status_code == 200


def test_metrics_content_type_is_prometheus():
    resp = client.get("/metrics")
    assert "text/plain" in resp.headers["content-type"]


def test_metrics_increments_after_request():
    client.get("/health")
    resp = client.get("/metrics")
    body = resp.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body


def test_metrics_error_counter_increments_on_4xx():
    client.post("/classify", json={"text": ""})  # triggers 422
    resp = client.get("/metrics")
    assert "http_errors_total" in resp.text
