"""
Deadline Intent Detector — determines whether a student's query is about deadlines.

Uses simple keyword + regex matching. No ML classifier needed for prototype.

IBM alignment: "Architect solutions to integrate LLMs with existing products"
(hybrid structured + unstructured retrieval)
"""

import re

DEADLINE_KEYWORDS = [
    "deadline",
    "due date",
    "last day",
    "when can i",
    "when do i",
    "add a course",
    "add course",
    "drop a course",
    "drop course",
    "withdraw",
    "register",
    "registration",
    "graduation application",
    "apply to graduate",
    "graduate",
    "commencement",
    "tuition",
    "payment",
    "fafsa",
    "regular module",
    "other module",
    "intensive",
    "weekend course",
    "late add",
    "late drop",
    "what happens if i miss",
    "w grade",
    "withdrawal",
    "refund",
    "capstone",
    "thesis deadline",
    "thesis proposal",
    "too late",
    "still possible",
    "can i still",
]

DEADLINE_PATTERNS = [
    r"when\s+(is|are|do|should|can)\s+.*(deadline|due|register|drop|add|withdraw|graduat)",
    r"(last|final)\s+day\s+(to|for)",
    r"what\s+happens\s+if\s+i\s+(miss|don't|forget|late)",
    r"(can|do)\s+i\s+still\s+(add|drop|withdraw|register|change)",
    r"(am\s+i|is\s+it)\s+(too\s+late|still\s+possible)",
    r"when\s+(do|should|must|can)\s+i\s+(apply|submit|register|graduate|enroll)",
]


def is_deadline_query(message: str) -> bool:
    """Return True if the query is deadline-related."""
    query_lower = message.lower()

    for keyword in DEADLINE_KEYWORDS:
        if keyword in query_lower:
            return True

    for pattern in DEADLINE_PATTERNS:
        if re.search(pattern, query_lower):
            return True

    return False
