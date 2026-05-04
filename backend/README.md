# AI Text Classifier API

FastAPI backend with rule-based text classification and RAG document Q&A.

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8000
```

API docs at http://localhost:8000/docs

## Test

```bash
pytest tests/ -v
```

## Endpoints

### GET /health

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### POST /classify

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "The API endpoint is returning a database error"}'
# {"category":"technical","confidence":0.8}

curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Our Q3 revenue strategy and KPI roadmap"}'
# {"category":"business","confidence":1.0}
```

### POST /upload *(Sprint 2+)*

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
# {"filename":"document.pdf","chunks_stored":12}
```

### POST /ask *(Sprint 2+)*

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?"}'
# {"answer":"...","sources":["chunk1","chunk2","chunk3"],"tool_trace":[]}
```

### GET /documents *(Sprint 2+)*

```bash
curl http://localhost:8000/documents
# {"documents":["document.pdf"]}
```

### GET /metrics *(Sprint 5+)*

```bash
curl http://localhost:8000/metrics
# Prometheus text format
```
