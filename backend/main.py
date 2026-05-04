import shutil
import time
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from pydantic import BaseModel, field_validator
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from classifier import classify
import rag as rag_module
from agent import run_agent

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".txt"}

app = FastAPI(title="AI Text Classifier + RAG Agent API", version="3.0.0")

# ---------- Prometheus metrics ----------

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["endpoint", "method"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint"],
)
ERROR_COUNT = Counter(
    "http_errors_total",
    "Total HTTP errors",
    ["endpoint", "status_code"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    endpoint = request.url.path
    method = request.method
    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start
    REQUEST_COUNT.labels(endpoint=endpoint, method=method).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    if response.status_code >= 400:
        ERROR_COUNT.labels(endpoint=endpoint, status_code=str(response.status_code)).inc()

    return response


# ---------- Request / Response models ----------

class ClassifyRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        if len(v) > 1000:
            raise ValueError("Text exceeds 1000 character limit")
        return v


class ClassifyResponse(BaseModel):
    category: str
    confidence: float


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    tool_trace: list[str] = []


class UploadResponse(BaseModel):
    filename: str
    chunks_stored: int


class DocumentsResponse(BaseModel):
    documents: list[str]


# ---------- Endpoints ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/classify", response_model=ClassifyResponse)
def classify_text(body: ClassifyRequest):
    category, confidence = classify(body.text)
    return ClassifyResponse(category=category, confidence=confidence)


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Only .pdf and .txt are allowed.",
        )

    save_path = UPLOAD_DIR / file.filename
    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks_stored = rag_module.ingest_file(save_path, file.content_type or "")
    return UploadResponse(filename=file.filename, chunks_stored=chunks_stored)


@app.post("/ask", response_model=AskResponse)
def ask_question(body: AskRequest):
    result = run_agent(body.question)
    return AskResponse(
        answer=result["answer"],
        sources=result["sources"],
        tool_trace=result["tool_trace"],
    )


@app.get("/documents", response_model=DocumentsResponse)
def get_documents():
    return DocumentsResponse(documents=rag_module.list_documents())
