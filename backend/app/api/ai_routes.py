from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, ConfigDict
from app.services.redis_store import RedisContextStore
from app.utils.nlp_utils import detect_sentiment, detect_intent
from app.utils.ai_utils import rag_ask
from app.utils.embeddings import chunk_text, build_or_update_index

router = APIRouter()

# Initialize Redis Store
STORE = RedisContextStore()

class TranscriptPayload(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    meeting_id: str = "default" # Default for demo
    speaker: str
    text: str
    timestamp: float | None = None

class AIRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    meeting_id: str = "default"
    message: str

def process_embeddings(meeting_id: str, text: str, speaker: str, timestamp: float):
    """Background task to update FAISS index"""
    chunks = chunk_text(text)
    metadata = [{"text": c, "speaker": speaker, "ts": timestamp} for c in chunks]
    build_or_update_index(meeting_id, chunks, metadata)

@router.post("/transcript/add")
async def add_transcript(payload: TranscriptPayload, background_tasks: BackgroundTasks):
    if not payload.text:
        raise HTTPException(status_code=400, detail="text required")

    # Add to Redis
    STORE.add_transcript(payload.meeting_id, payload.speaker, payload.text, payload.timestamp)

    # Auto-detect sentiment & intent
    sentiment = detect_sentiment(payload.text)
    STORE.add_sentiment(payload.meeting_id, payload.text, sentiment)

    intent = detect_intent(payload.text)
    STORE.add_speaker_intent(payload.meeting_id, payload.text, intent)

    # Detect action items
    low = payload.text.lower()
    if "action:" in low or any(w in low for w in ["todo", "do by", "due:"]):
        STORE.add_action_item(payload.meeting_id, payload.text, owner=None)

    # Trigger embedding update in background
    background_tasks.add_task(
        process_embeddings, 
        payload.meeting_id, 
        payload.text, 
        payload.speaker, 
        payload.timestamp or 0.0
    )

    return {"status": "ok"}

@router.post("/respond")
async def ai_respond(req: AIRequest):
    # Use RAG flow
    response = rag_ask(req.meeting_id, req.message, STORE)
    return {"response": response}
