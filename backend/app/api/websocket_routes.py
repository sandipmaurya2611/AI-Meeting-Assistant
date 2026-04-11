from fastapi import APIRouter, WebSocket, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Optional
import logging

from app.services.websocket_service import websocket_manager, push_ai_suggestion
from app.services.copilot_service import MeetingCopilot
from app.services.redis_store import RedisContextStore
from app.rag.vector_store import get_vector_store
from app.rag.rag_engine import RAGEngine

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
copilot = MeetingCopilot()
context_store = RedisContextStore()
vector_store = get_vector_store()
rag_engine = RAGEngine(vector_store)


class TranscriptProcessRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    transcript: str
    meeting_id: Optional[str] = "default"
    speaker: Optional[str] = "Unknown"
    use_rag: Optional[bool] = True
    top_k: Optional[int] = 3


@router.websocket("/ws/ai")
async def ai_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time AI suggestions.
    
    Clients connect to: ws://localhost:8000/ws/ai
    
    The server will push AI suggestions in real-time as they are generated.
    
    Message format:
    {
        "suggestion": "Your next sentence...",
        "follow_up_question": "Question to ask...",
        "confusion_detected": false,
        "talking_points": ["Point 1", "Point 2"],
        "crm_update": "Update CRM...",
        "task_creation": "Create task...",
        "timestamp": "2025-11-28T00:00:00"
    }
    """
    await websocket_manager(websocket)


@router.post("/process-transcript")
async def process_transcript(request: TranscriptProcessRequest):
    """
    Process transcript and generate AI suggestions.
    
    Pipeline:
    1. Receive transcript and context
    2. Perform RAG search (if enabled)
    3. Build AI agent prompt
    4. Call LLM (Groq)
    5. Parse structured response
    6. Push result into ai_queue
    7. WebSocket broadcasts to all clients
    
    Input:
    {
        "transcript": "The client is asking about pricing",
        "meeting_id": "meeting_123",
        "speaker": "Client",
        "use_rag": true,
        "top_k": 3
    }
    
    Output:
    {
        "status": "ok",
        "message": "AI suggestion generated and pushed to WebSocket"
    }
    """
    try:
        import datetime
        
        # Step 1: Get context from Redis
        context = context_store.get_context(request.meeting_id)
        logger.info(f"Retrieved context for meeting: {request.meeting_id}")
        
        # Step 2: Perform RAG search
        rag_results = []
        if request.use_rag:
            search_result = rag_engine.get_relevant_context(
                query=request.transcript,
                top_k=request.top_k
            )
            rag_results = search_result.get('chunks', [])
            logger.info(f"RAG search returned {len(rag_results)} results")
        
        # Step 3 & 4: Generate AI suggestion using copilot
        copilot_response = copilot.get_copilot_suggestion(
            transcript=request.transcript,
            context=context,
            rag_results=rag_results
        )
        logger.info("AI suggestion generated successfully")
        
        # Step 5: Format response for WebSocket
        ai_result = {
            "suggestion": copilot_response.suggestion,
            "follow_up_question": copilot_response.follow_up_question,
            "confusion_detected": copilot_response.confusion_detected.lower() == "yes" if copilot_response.confusion_detected else False,
            "talking_points": copilot_response.talking_points,
            "crm_update": copilot_response.crm_update,
            "task_creation": copilot_response.task_creation,
            "timestamp": datetime.datetime.now().isoformat(),
            "meeting_id": request.meeting_id,
            "speaker": request.speaker
        }
        
        # Step 6: Push to queue (WebSocket will broadcast automatically)
        push_ai_suggestion(ai_result)
        logger.info("AI suggestion pushed to WebSocket queue")
        
        # Optional: Add transcript to context store for future reference
        if request.transcript:
            context_store.add_transcript(
                meeting_id=request.meeting_id,
                speaker=request.speaker,
                text=request.transcript
            )
        
        return {
            "status": "ok",
            "message": "AI suggestion generated and pushed to WebSocket",
            "preview": {
                "suggestion": copilot_response.suggestion[:50] + "..." if len(copilot_response.suggestion) > 50 else copilot_response.suggestion
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
