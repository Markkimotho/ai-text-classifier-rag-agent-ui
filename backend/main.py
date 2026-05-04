from fastapi import FastAPI
from pydantic import BaseModel, field_validator

from classifier import classify

app = FastAPI(title="AI Text Classifier API", version="1.0.0")


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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classify", response_model=ClassifyResponse)
def classify_text(body: ClassifyRequest):
    category, confidence = classify(body.text)
    return ClassifyResponse(category=category, confidence=confidence)
