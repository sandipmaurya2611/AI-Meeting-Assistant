from typing import List, Dict, Any
from collections import deque
import time

class ContextManager:
    def __init__(self, max_history: int = 200):
        # keep a deque for efficient pops from left
        self.history: deque[str] = deque(maxlen=max_history)
        self.action_items: List[Dict[str, Any]] = []
        self.meeting_topic: str | None = None
        self.sentiments: deque[tuple] = deque(maxlen=50)
        self.speaker_intents: deque[tuple] = deque(maxlen=100)
        self.metadata: Dict[str, Any] = {}

    # Topic
    def set_topic(self, topic: str):
        self.meeting_topic = topic
        self._add_metadata("topic_set_at", time.time())

    # Basic transcript add
    def add_transcript(self, speaker: str, text: str, timestamp: float | None = None):
        if timestamp is None:
            timestamp = time.time()
        entry = {"speaker": speaker, "text": text, "ts": timestamp}
        self.history.append(entry)

    def add_action_item(self, title: str, owner: str | None = None, due: str | None = None):
        item = {"title": title, "owner": owner, "due": due, "created_at": time.time(), "done": False}
        self.action_items.append(item)
        return item

    def mark_action_done(self, idx: int):
        if 0 <= idx < len(self.action_items):
            self.action_items[idx]["done"] = True
            return True
        return False

    def add_sentiment(self, text: str, sentiment: str):
        self.sentiments.append((text, sentiment, time.time()))

    def add_speaker_intent(self, text: str, intent: str):
        self.speaker_intents.append((text, intent, time.time()))

    def _add_metadata(self, k: str, v: Any):
        self.metadata[k] = v

    def get_context(self, last_n: int = 15) -> Dict[str, Any]:
        last_history = list(self.history)[-last_n:]
        return {
            "topic": self.meeting_topic,
            "last_history": last_history,
            "action_items": self.action_items,
            "recent_sentiments": list(self.sentiments),
            "recent_intents": list(self.speaker_intents),
            "metadata": self.metadata,
        }

    def clear(self):
        self.history.clear()
        self.action_items.clear()
        self.sentiments.clear()
        self.speaker_intents.clear()
        self.metadata.clear()
