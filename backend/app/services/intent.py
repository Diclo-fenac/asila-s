from __future__ import annotations

from dataclasses import dataclass


DEPARTMENT_KEYWORDS = {
    "health": {"vaccination", "hospital", "clinic", "covid", "immunization"},
    "electricity": {"power", "outage", "electricity", "transformer"},
    "water": {"water", "pipeline", "tap", "supply"},
    "municipality": {"garbage", "waste", "streetlight", "sanitation"},
}


@dataclass
class IntentResult:
    department: str | None
    matched_keywords: set[str]


def classify_intent(message: str) -> IntentResult:
    normalized = message.lower()
    for department, keywords in DEPARTMENT_KEYWORDS.items():
        matched = {kw for kw in keywords if kw in normalized}
        if matched:
            return IntentResult(department=department, matched_keywords=matched)
    return IntentResult(department=None, matched_keywords=set())
