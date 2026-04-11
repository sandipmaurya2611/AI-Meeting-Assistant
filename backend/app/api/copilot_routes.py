from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
import logging

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


class CopilotRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    transcript: str
    meeting_id: Optional[str] = "default"
    use_rag: Optional[bool] = True
    top_k: Optional[int] = 3


class CopilotResponse(BaseModel):
    suggestion: str
    follow_up_question: str
    confusion_detected: bool
    talking_points: List[str]
    crm_update: str
    task_creation: str
    raw_response: Optional[str] = None


@router.post("/copilot", response_model=CopilotResponse)
async def get_copilot_suggestion(request: CopilotRequest):
    """
    Real-Time AI Meeting Co-Pilot
    
    Analyzes the current transcript and provides:
    - Next sentence suggestion (max 20 words)
    - Follow-up question
    - Confusion detection
    - Talking points
    - CRM update suggestion
    - Task creation suggestion
    
    Input:
    {
        "transcript": "The client is asking about our pricing",
        "meeting_id": "meeting_123",
        "use_rag": true,
        "top_k": 3
    }
    
    Output:
    {
        "suggestion": "Our pricing starts at $49/month and scales with your team size.",
        "follow_up_question": "Would you like to hear about our volume discounts?",
        "confusion_detected": false,
        "talking_points": [
            "Standard plan: $49/user/month",
            "Volume discounts available",
            "14-day free trial included"
        ],
        "crm_update": "Client interested in pricing - send proposal",
        "task_creation": "Send pricing PDF and schedule follow-up call"
    }
    """
    try:
        # Get context from Redis
        context = context_store.get_context(request.meeting_id)
        
        # Get RAG results if enabled
        rag_results = []
        if request.use_rag:
            search_result = rag_engine.get_relevant_context(
                query=request.transcript,
                top_k=request.top_k
            )
            rag_results = search_result.get('chunks', [])
        
        # Get copilot suggestions
        copilot_response = copilot.get_copilot_suggestion(
            transcript=request.transcript,
            context=context,
            rag_results=rag_results
        )
        
        return copilot_response.to_dict()
        
    except Exception as e:
        logger.error(f"Error in copilot endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/simple")
async def get_simple_copilot_suggestion(request: CopilotRequest):
    """
    Simplified copilot endpoint without context/RAG
    
    Use this for quick suggestions based only on the transcript.
    """
    try:
        copilot_response = copilot.get_copilot_suggestion(
            transcript=request.transcript,
            context=None,
            rag_results=None
        )
        
        return copilot_response.to_dict()
        
    except Exception as e:
        logger.error(f"Error in simple copilot endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
