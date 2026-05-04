"""
LangChain-compatible agent with ReAct-style tool routing, conversation memory,
and four built-in tools. Avoids AgentExecutor (removed in langchain 1.x) in
favour of a self-contained loop that works with any LangChain/LangGraph version.
"""

from __future__ import annotations

import re
from collections import deque
from datetime import datetime, timezone
from typing import Any

import rag as rag_module

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _calculator(expression: str) -> str:
    """Evaluate a numeric math expression safely."""
    expr = re.sub(r"[^0-9+\-*/().\s]", "", expression).strip()
    if not expr:
        return "Invalid expression — only numeric operations are supported."
    try:
        result = eval(expr, {"__builtins__": {}})  # noqa: S307 — numeric-only whitelist
        return str(round(float(result), 6))
    except Exception as e:
        return f"Calculation error: {e}"


def _current_time(_: str) -> str:
    """Return the current UTC time."""
    return datetime.now(timezone.utc).isoformat()


def _web_search_mock(query: str) -> str:
    """Return deterministic simulated web search results."""
    results = [
        {
            "title": "LLM Advances in 2024 — AI Research Digest",
            "snippet": "Large language models continue to improve in reasoning, code generation, and multimodal capabilities.",
            "url": "https://example.com/llm-2024",
        },
        {
            "title": "Open-Source AI Tools Roundup",
            "snippet": "A curated list of open-source LLM tools including LangChain, LlamaIndex, and sentence-transformers.",
            "url": "https://example.com/open-source-ai",
        },
        {
            "title": "RAG Systems: Best Practices",
            "snippet": "Retrieval-augmented generation improves factual accuracy by grounding LLM responses in external documents.",
            "url": "https://example.com/rag-best-practices",
        },
    ]
    lines = "\n".join(f"[{r['title']}] {r['snippet']} ({r['url']})" for r in results)
    return f"Mock web search results for '{query}':\n{lines}"


def _document_qa(question: str) -> tuple[str, list[str]]:
    """Retrieve relevant chunks and generate an answer."""
    chunks = rag_module.retrieve(question)
    answer = rag_module.generate_answer(question, chunks)
    return answer, chunks


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

_TOOLS: dict[str, dict] = {
    "Calculator": {
        "fn": _calculator,
        "description": "Evaluate numeric math expressions. Trigger on math questions with numbers.",
        "keywords": [],  # handled by numeric regex
    },
    "Current Time": {
        "fn": _current_time,
        "description": "Return current UTC datetime.",
        "keywords": ["time", "date", "today", "now", "current time", "what time"],
    },
    "Web Search Mock": {
        "fn": _web_search_mock,
        "description": "Simulated web search. Use for news, online, internet, latest questions.",
        "keywords": ["news", "latest", "search", "web", "internet", "online"],
    },
    "Document Q&A": {
        "fn": _document_qa,
        "description": "Answer questions from uploaded documents using RAG.",
        "keywords": ["document", "doc", "file", "upload", "says", "according", "content"],
    },
}

_MATH_RE = re.compile(r"\d[\d\s]*[+\-*/][\d\s]")


def _select_tool(question: str) -> str | None:
    """Pick the best tool for a question using keyword + pattern heuristics."""
    q = question.lower()

    # Math: must contain a number AND an operator
    if _MATH_RE.search(q) and any(kw in q for kw in ["what is", "calculate", "compute", "multiply", "divide", "plus", "minus", "sum"]):
        return "Calculator"
    if _MATH_RE.search(q) and ("?" in question or any(op in q for op in ["+", "-", "*", "/"])):
        return "Calculator"

    for name, meta in _TOOLS.items():
        if any(kw in q for kw in meta["keywords"]):
            return name

    # Fall back to Document Q&A when documents are loaded
    if rag_module.list_documents():
        return "Document Q&A"

    return None  # answer directly


# ---------------------------------------------------------------------------
# Conversation memory (global single session, k=5)
# ---------------------------------------------------------------------------

_memory: deque[tuple[str, str]] = deque(maxlen=5)


def _build_context() -> str:
    if not _memory:
        return ""
    lines = []
    for q, a in _memory:
        lines.append(f"User: {q}")
        lines.append(f"Assistant: {a}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public agent interface
# ---------------------------------------------------------------------------

MAX_ITERATIONS = 5


def run_agent(question: str) -> dict[str, Any]:
    tool_trace: list[str] = []
    doc_sources: list[str] = []
    answer = ""

    context = _build_context()
    full_question = f"{context}\nUser: {question}" if context else question

    for _ in range(MAX_ITERATIONS):
        tool_name = _select_tool(full_question if not tool_trace else question)

        if tool_name is None:
            answer = _direct_answer(question, context)
            break

        tool_trace.append(tool_name)
        tool_fn = _TOOLS[tool_name]["fn"]

        if tool_name == "Document Q&A":
            answer, doc_sources = tool_fn(question)
        else:
            answer = tool_fn(question)

        # One tool call is enough for these deterministic tools
        break

    if not answer:
        answer = _direct_answer(question, context)

    _memory.append((question, answer))

    return {
        "answer": answer,
        "tool_trace": tool_trace,
        "sources": doc_sources,
    }


def _direct_answer(question: str, context: str) -> str:
    q = question.lower().strip().rstrip("?")

    if context:
        # Look for references to previous turn
        for q_prev, a_prev in _memory:
            if any(word in question.lower() for word in q_prev.lower().split() if len(word) > 4):
                return f"Based on our conversation: {a_prev}"

    if any(kw in q for kw in ["hello", "hi there", "hey"]):
        return "Hello! How can I help you today?"
    if "your name" in q or "who are you" in q:
        return "I am an AI document assistant powered by a RAG pipeline and LangChain tools."
    if "help" in q or "what can you do" in q:
        return (
            "I can help with: document Q&A (upload a .pdf or .txt), "
            "math calculations, current time, and simulated web searches."
        )
    return (
        f"I don't have specific information about '{question}'. "
        "Try uploading a document, or ask me to calculate something or check the time."
    )


def reset_memory() -> None:
    _memory.clear()
