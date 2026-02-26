"""
Deadline Personalizer — asks clarifying questions when needed for deadline queries.

For deadline queries about course actions (add/drop/withdraw), we need to know
whether the student is in a Regular Module or Other Module course, because the
deadlines are different.

Scoped to MS students only — no program-type question needed.
"""

MODULE_TERMS = [
    "regular module",
    "other module",
    "intensive",
    "weekend",
    "full semester",
    "16 week",
    "8 week",
    "accelerated",
    "regular",
    "full term",
]

COURSE_ACTION_TERMS = [
    "add",
    "drop",
    "withdraw",
    "register",
    "course",
    "class",
    "enroll",
]


def get_clarifying_question(
    user_query: str, conversation_history: list[dict]
) -> str | None:
    """
    Returns a clarifying question if we need more info before answering,
    or None if we can proceed directly.

    Currently checks: for course add/drop/withdraw queries, do we know the module type?
    """
    query_lower = user_query.lower()
    history_text = " ".join(
        msg.get("content", "").lower() for msg in conversation_history
    )

    is_course_action = any(term in query_lower for term in COURSE_ACTION_TERMS)
    module_already_known = any(
        term in query_lower or term in history_text for term in MODULE_TERMS
    )

    if is_course_action and not module_already_known:
        return (
            "Just to give you the right deadline — is this for a **regular "
            "full-semester course** (16 weeks, listed as 'Regular Module' in the "
            "portal), or an **intensive/weekend/accelerated course** (Other Module)? "
            "These have different deadlines."
        )

    return None
