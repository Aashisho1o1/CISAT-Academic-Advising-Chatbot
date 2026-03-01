"""
Hallucination Detection Pipeline — LLM-as-Judge faithfulness scoring.

For every chatbot response, this module evaluates whether the response is
grounded in the retrieved source documents or contains fabricated claims.

IBM alignment: "Establish evaluation datasets and benchmarks to measure LLM
performance" + "Develop monitoring systems to track model performance"
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from openai_client import get_async_client

logger = logging.getLogger("hallucination_detector")

EVAL_LOG_PATH = Path(__file__).parent.parent / "evaluation_logs" / "hallucination_log.jsonl"

FAITHFULNESS_PROMPT = """
You are an evaluation judge for an academic advising chatbot at Claremont Graduate University (CGU), specifically for MS students in the CISAT program.

Your task: Determine whether the chatbot's response is faithfully grounded in the provided source documents.

## Source Documents (Retrieved Context)
{retrieved_chunks}

## Student's Question
{user_query}

## Chatbot's Response
{chatbot_response}

## Your Task
1. Break the chatbot's response into individual claims (factual statements).
2. For each claim, determine:
   - SUPPORTED: Directly supported by the source documents
   - PARTIALLY_SUPPORTED: Related to source content but adds interpretation or extrapolation
   - NOT_SUPPORTED: No basis in source documents (hallucination)
   - NOT_APPLICABLE: General statement, greeting, or meta-comment not requiring source support

3. Pay special attention to:
   - Dates and deadlines (these MUST be exactly correct)
   - Course requirements and prerequisites
   - GPA requirements and policies
   - Anything about fees, costs, or financial consequences

4. Return your analysis as JSON:
{{
  "claims": [
    {{
      "claim_text": "the specific claim from the response",
      "verdict": "SUPPORTED | PARTIALLY_SUPPORTED | NOT_SUPPORTED | NOT_APPLICABLE",
      "evidence": "Quote or reference from source docs, or N/A",
      "reasoning": "Brief explanation"
    }}
  ],
  "overall_faithfulness_score": <float 0.0 to 1.0>,
  "overall_verdict": "grounded | partially_grounded | hallucinated",
  "high_risk_flags": ["list any claims about dates, GPA, fees, or requirements that are NOT_SUPPORTED"]
}}

Scoring guide:
- 1.0 = All substantive claims are SUPPORTED
- 0.7-0.9 = Most claims supported, minor extrapolations
- 0.4-0.6 = Mix of supported and unsupported claims
- 0.0-0.3 = Majority of claims are NOT_SUPPORTED
"""


async def check_faithfulness(
    user_query: str,
    chatbot_response: str,
    retrieved_chunks: list[str],
) -> dict:
    """
    Evaluate a chatbot response for hallucination using LLM-as-Judge (async).

    Returns a dict with:
        - overall_faithfulness_score (float 0.0-1.0)
        - overall_verdict ("grounded" | "partially_grounded" | "hallucinated")
        - claims (list of per-claim verdicts)
        - high_risk_flags (list of unsupported claims about dates/GPA/fees)
        - flagged (bool — True if score < 0.7 or high_risk_flags exist)

    Never raises — returns a safe default on any error so the response always goes through.
    """
    safe_default = {
        "overall_faithfulness_score": None,
        "overall_verdict": "evaluation_unavailable",
        "claims": [],
        "high_risk_flags": [],
        "flagged": True,
        "error": None,
    }

    try:
        client = get_async_client()

        formatted_chunks = "\n\n".join(
            f"[Source {i + 1}]: {chunk}" for i, chunk in enumerate(retrieved_chunks)
        )

        prompt = FAITHFULNESS_PROMPT.format(
            retrieved_chunks=formatted_chunks or "[No source documents retrieved]",
            user_query=user_query,
            chatbot_response=chatbot_response,
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise evaluation judge. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)

        score = result.get("overall_faithfulness_score", 1.0)
        high_risk = result.get("high_risk_flags", [])
        flagged = score < 0.7 or len(high_risk) > 0

        return {
            "overall_faithfulness_score": score,
            "overall_verdict": result.get("overall_verdict", "unknown"),
            "claims": result.get("claims", []),
            "high_risk_flags": high_risk,
            "flagged": flagged,
            "error": None,
        }

    except Exception as e:
        safe_default["error"] = str(e)
        logger.error("Evaluation failed (non-blocking): %s", e)
        return safe_default


def _sanitize_log_field(value: list | str) -> list | str:
    """Sanitize LLM-generated fields before writing to log files."""
    if isinstance(value, list):
        return [str(item)[:500] for item in value[:20]]  # cap list size and item length
    if isinstance(value, str):
        return value[:1000]
    return str(value)[:1000]


def log_evaluation(
    user_query: str,
    chatbot_response: str,
    faith_result: dict,
) -> None:
    """Append a redacted faithfulness evaluation result to the JSONL log file.

    Stores only a SHA-256 hash of the query and response length — no raw
    student text is persisted, avoiding FERPA/PII exposure in log files.
    """
    try:
        EVAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query_hash": hashlib.sha256(user_query.encode()).hexdigest()[:16],
            "response_length": len(chatbot_response),
            "faithfulness_score": faith_result.get("overall_faithfulness_score"),
            "verdict": faith_result.get("overall_verdict"),
            "flagged": faith_result.get("flagged", False),
            "high_risk_flags": _sanitize_log_field(faith_result.get("high_risk_flags", [])),
            "num_unsupported_claims": len(
                [
                    c
                    for c in faith_result.get("claims", [])
                    if c.get("verdict") == "NOT_SUPPORTED"
                ]
            ),
            "error": faith_result.get("error"),
        }
        with open(EVAL_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=True) + "\n")
    except Exception as e:
        logger.error("Logging failed: %s", e)
