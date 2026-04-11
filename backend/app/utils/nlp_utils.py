# lightweight rules-based sentiment & intent detection (replaceable with ML models)

QUESTION_WORDS = ["who","what","when","where","why","how","is","are","do","did","does","should"]


def detect_sentiment(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["great", "good", "thanks", "awesome", "excellent"]):
        return "positive"
    if any(w in t for w in ["not good", "problem", "issue", "angry", "frustrat"]):
        return "negative"
    return "neutral"


def detect_intent(text: str) -> str:
    t = text.strip()
    low = t.lower()
    if t.endswith("?") or any(low.startswith(w + " ") for w in QUESTION_WORDS):
        return "question"
    if any(x in low for x in ["let's", "lets", "we should", "we will", "we'll"]):
        return "planning"
    if any(x in low for x in ["i will", "i'll", "assign", "action"]):
        return "action"
    if any(x in low for x in ["agree", "sounds good", "ok", "okay", "confirm"]):
        return "confirmation"
    return "statement"
