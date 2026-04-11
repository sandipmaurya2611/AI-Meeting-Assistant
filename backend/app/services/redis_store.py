import json
import time
from typing import List, Dict, Any, Optional
import redis
from app.core.config import settings


class InMemoryRedis:
    """Lightweight in-memory fallback when Redis is unavailable."""
    def __init__(self):
        self._store = {}
    def rpush(self, key, value):
        self._store.setdefault(key, []).append(value)
    def lrange(self, key, start, end):
        lst = self._store.get(key, [])
        if end == -1:
            return lst[start:]
        return lst[start:end+1]
    def ltrim(self, key, start, end):
        lst = self._store.get(key, [])
        self._store[key] = lst[start:] if end == -1 else lst[start:end+1]
    def hset(self, name, key=None, value=None, mapping=None):
        self._store.setdefault(name, {})
        if mapping:
            self._store[name].update(mapping)
        if key is not None:
            self._store[name][key] = value
    def hgetall(self, key):
        return self._store.get(key, {})
    def expire(self, key, ttl):
        pass
    def delete(self, *keys):
        for k in keys:
            self._store.pop(k, None)
    def ping(self):
        return True


class RedisContextStore:
    def __init__(self):
        self._redis = None
        self.ttl = 86400 * 7  # 7 days retention for demo
    
    @property
    def redis(self):
        """Lazy-load Redis connection. Falls back to in-memory store."""
        if self._redis is None:
            try:
                self._redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
                # Test connection
                self._redis.ping()
                print("✅ Redis connected successfully")
            except Exception as e:
                print(f"⚠️  Redis unavailable ({e}). Using in-memory fallback.")
                self._redis = InMemoryRedis()
        return self._redis

    def _key_history(self, meeting_id: str) -> str:
        return f"meeting:{meeting_id}:history"

    def _key_actions(self, meeting_id: str) -> str:
        return f"meeting:{meeting_id}:actions"

    def _key_meta(self, meeting_id: str) -> str:
        return f"meeting:{meeting_id}:meta"
    
    def _key_sentiments(self, meeting_id: str) -> str:
        return f"meeting:{meeting_id}:sentiments"
    
    def _key_intents(self, meeting_id: str) -> str:
        return f"meeting:{meeting_id}:intents"

    def add_transcript(self, meeting_id: str, speaker: str, text: str, timestamp: float | None = None):
        if timestamp is None:
            timestamp = time.time()
        
        entry = {
            "speaker": speaker,
            "text": text,
            "ts": timestamp
        }
        
        # Push to right (end) of list
        key = self._key_history(meeting_id)
        self.redis.rpush(key, json.dumps(entry))
        self.redis.expire(key, self.ttl)
        
        # Update metadata last_updated
        self.redis.hset(self._key_meta(meeting_id), "last_updated", timestamp)

    def add_action_item(self, meeting_id: str, title: str, owner: str | None = None, due: str | None = None):
        item = {
            "title": title, 
            "owner": owner, 
            "due": due, 
            "created_at": time.time(), 
            "done": False
        }
        key = self._key_actions(meeting_id)
        self.redis.rpush(key, json.dumps(item))
        self.redis.expire(key, self.ttl)
        return item

    def add_sentiment(self, meeting_id: str, text: str, sentiment: str):
        entry = {"text": text, "sentiment": sentiment, "ts": time.time()}
        key = self._key_sentiments(meeting_id)
        self.redis.rpush(key, json.dumps(entry))
        self.redis.ltrim(key, -50, -1) # Keep last 50
        self.redis.expire(key, self.ttl)

    def add_speaker_intent(self, meeting_id: str, text: str, intent: str):
        entry = {"text": text, "intent": intent, "ts": time.time()}
        key = self._key_intents(meeting_id)
        self.redis.rpush(key, json.dumps(entry))
        self.redis.ltrim(key, -100, -1) # Keep last 100
        self.redis.expire(key, self.ttl)

    def set_topic(self, meeting_id: str, topic: str):
        self.redis.hset(self._key_meta(meeting_id), mapping={"topic": topic, "topic_set_at": time.time()})

    def get_context(self, meeting_id: str, last_n: int = 15) -> Dict[str, Any]:
        # Get history
        hist_raw = self.redis.lrange(self._key_history(meeting_id), -last_n, -1)
        history = [json.loads(x) for x in hist_raw]
        
        # Get actions
        actions_raw = self.redis.lrange(self._key_actions(meeting_id), 0, -1)
        action_items = [json.loads(x) for x in actions_raw]
        
        # Get metadata
        meta = self.redis.hgetall(self._key_meta(meeting_id))
        
        # Get recent sentiments/intents
        sent_raw = self.redis.lrange(self._key_sentiments(meeting_id), 0, -1)
        sentiments = [json.loads(x) for x in sent_raw]
        
        intents_raw = self.redis.lrange(self._key_intents(meeting_id), 0, -1)
        intents = [json.loads(x) for x in intents_raw]

        return {
            "topic": meta.get("topic"),
            "last_history": history,
            "action_items": action_items,
            "recent_sentiments": sentiments,
            "recent_intents": intents,
            "metadata": meta,
        }

    def clear_meeting(self, meeting_id: str):
        keys = [
            self._key_history(meeting_id),
            self._key_actions(meeting_id),
            self._key_meta(meeting_id),
            self._key_sentiments(meeting_id),
            self._key_intents(meeting_id)
        ]
        self.redis.delete(*keys)
