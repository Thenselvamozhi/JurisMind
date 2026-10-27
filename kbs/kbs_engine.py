import json
import os
from rapidfuzz import fuzz, process

# Load the Knowledge Base
KBS_PATH = os.path.join(os.path.dirname(__file__), "../data/legal_kbs.json")

with open(KBS_PATH, "r") as f:
    KBS_DATA = json.load(f)


def search_kbs(user_query: str, threshold: int = 55) -> dict:
    """
    Search the Knowledge Base System for the best matching answer.
    Uses fuzzy matching on keywords and questions.
    Returns best match or fallback message.
    """
    user_query_lower = user_query.lower()
    best_score = 0
    best_entry = None

    for entry in KBS_DATA:
        # Match against question
        q_score = fuzz.partial_ratio(user_query_lower, entry["question"].lower())

        # Match against each keyword
        kw_scores = [
            fuzz.partial_ratio(user_query_lower, kw.lower())
            for kw in entry["keywords"]
        ]
        kw_score = max(kw_scores) if kw_scores else 0

        # Match against answer text
        ans_score = fuzz.partial_ratio(user_query_lower, entry["answer"].lower()) * 0.6

        combined_score = max(q_score, kw_score, ans_score)

        if combined_score > best_score:
            best_score = combined_score
            best_entry = entry

    if best_entry and best_score >= threshold:
        return {
            "found": True,
            "score": round(best_score, 2),
            "intent": best_entry["intent"],
            "question": best_entry["question"],
            "answer": best_entry["answer"],
        }
    else:
        return {
            "found": False,
            "score": best_score,
            "intent": "unknown",
            "question": None,
            "answer": None,
        }


def get_all_intents() -> list:
    """Returns list of all unique intents in KBS."""
    return list(set(entry["intent"] for entry in KBS_DATA))


def get_entries_by_intent(intent: str) -> list:
    """Returns all KBS entries for a given intent."""
    return [e for e in KBS_DATA if e["intent"] == intent]
