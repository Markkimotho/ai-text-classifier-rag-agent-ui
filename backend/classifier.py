from typing import Tuple

KEYWORDS: dict[str, list[str]] = {
    "technical": [
        "api", "function", "database", "code", "error", "server", "deploy",
        "framework", "library", "bug", "endpoint", "query", "algorithm",
        "repository", "syntax", "compiler", "runtime", "latency", "debug",
    ],
    "business": [
        "revenue", "client", "strategy", "meeting", "budget", "kpi",
        "stakeholder", "roadmap", "proposal", "contract", "profit", "loss",
        "quarterly", "forecast", "pipeline", "conversion", "onboarding",
    ],
    "casual": [
        "hey", "thanks", "cool", "weekend", "lunch", "movie", "lol",
        "sounds good", "catch up", "later", "awesome", "sure", "chat",
        "hang out", "drinks", "dinner", "party", "chill", "vibe",
    ],
}

THRESHOLD = 1  # minimum matches required to claim a category


def classify(text: str) -> Tuple[str, float]:
    lower = text.lower()
    scores: dict[str, int] = {}

    for category, keywords in KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in lower)
        if count > 0:
            scores[category] = count

    if not scores:
        return "other", 0.0

    winner = max(scores, key=lambda c: scores[c])
    total_signals = sum(scores.values())
    confidence = round(scores[winner] / total_signals, 2)

    return winner, confidence
