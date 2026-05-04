import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, field_validator

from classifier import classify
import rag as rag_module

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
    "application/octet-stream",  # Some clients send this for .txt
}
ALLOWED_EXTENSIONS = {".pdf", ".txt"}

app = FastAPI(title="AI Text Classifier + RAG API", version="2.0.0")


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


@app.post("/classify", response_model=ClassifyResponse)
def classify_text(body: ClassifyRequest):
    category, confidence = classify(body.text)
    return ClassifyResponse(category=category, confidence=confidence)


@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}. Only .pdf and .txt are allowed.")

    save_path = UPLOAD_DIR / file.filename
    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    chunks_stored = rag_module.ingest_file(save_path, file.content_type or "")
    return UploadResponse(filename=file.filename, chunks_stored=chunks_stored)


@app.post("/ask", response_model=AskResponse)
def ask_question(body: AskRequest):
    chunks = rag_module.retrieve(body.question)
    answer = rag_module.generate_answer(body.question, chunks)
    return AskResponse(answer=answer, sources=chunks)


@app.get("/documents", response_model=DocumentsResponse)
def get_documents():
    return DocumentsResponse(documents=rag_module.list_documents())
