from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import asyncio
import logging
import json
from typing import Optional
from app.services.deepgram_service import deepgram_service
from app.services.transcript_service import save_transcript

router = APIRouter()
logger = logging.getLogger(__name__)

class WebSocketAdapter:
    """
    Adapter to intercept messages sent to the websocket, 
    allowing us to save transcripts to the DB.
    """
    def __init__(self, websocket: WebSocket, meeting_id: Optional[str]):
        self.websocket = websocket
        self.meeting_id = meeting_id

    async def send_text(self, text: str):
        # Intercept to save to DB
        if self.meeting_id:
            try:
                data = json.loads(text)
                if data.get("type") == "transcript" and data.get("is_final"):
                    # Fire and forget save
                    asyncio.create_task(save_transcript(
                        meeting_id=self.meeting_id,
                        speaker="User", # TODO: Use diarization from Deepgram if available
                        text=data["text"],
                        timestamp=None # Let DB handle current timestamp
                    ))
            except Exception as e:
                logger.error(f"Error processing transcript for save: {e}")
        
        # Forward to actual websocket
        await self.websocket.send_text(text)

@router.websocket("/ws-transcript")
async def websocket_endpoint(websocket: WebSocket, meeting_id: Optional[str] = Query(None)):
    await websocket.accept()
    logger.info(f"WebSocket connected. Meeting ID: {meeting_id}")
    
    audio_queue = asyncio.Queue()
    adapter = WebSocketAdapter(websocket, meeting_id)
    
    # Start Deepgram streaming task
    deepgram_task = asyncio.create_task(
        deepgram_service.transcribe_stream(audio_queue, adapter)
    )
    
    try:
        while True:
            # Receive audio chunk from frontend
            # We expect raw bytes (PCM 16-bit, 16kHz)
            data = await websocket.receive_bytes()
            await audio_queue.put(data)
            
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Signal Deepgram service to stop
        await audio_queue.put(None)
        await deepgram_task
