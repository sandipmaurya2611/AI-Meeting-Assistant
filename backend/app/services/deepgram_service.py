import asyncio
import json
import logging
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

class DeepgramService:
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        if not self.api_key:
            logger.error("DEEPGRAM_API_KEY is not set")

    async def transcribe_stream(self, audio_queue: asyncio.Queue, websocket):
        """
        Reads audio chunks from audio_queue and streams to Deepgram.
        Sends transcripts back to the websocket.
        """
        try:
            # Initialize Deepgram Client
            deepgram = DeepgramClient(self.api_key)
            
            # Create a websocket connection to Deepgram
            # Note: listen.async_live.v("1") creates an async client
            dg_connection = deepgram.listen.async_live.v("1")

            # Define event handlers
            async def on_message(self, result, **kwargs):
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) == 0:
                    return
                
                response = {
                    "type": "transcript",
                    "text": sentence,
                    "is_final": result.is_final,
                    "timestamp": result.start
                }
                
                # Send to frontend
                try:
                    await websocket.send_text(json.dumps(response))
                except Exception as e:
                    logger.error(f"Error sending to websocket: {e}")

            async def on_metadata(self, metadata, **kwargs):
                pass

            async def on_error(self, error, **kwargs):
                logger.error(f"Deepgram Error: {error}")

            # Register handlers
            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
            dg_connection.on(LiveTranscriptionEvents.Error, on_error)

            # Configure Options
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                smart_format=True,
                encoding="linear16",
                channels=1,
                sample_rate=16000,
                interim_results=True,
                utterance_end_ms="1000",
                vad_events=True,
            )

            # Start the connection
            if await dg_connection.start(options) is False:
                logger.error("Failed to connect to Deepgram")
                await websocket.send_text(json.dumps({"type": "error", "message": "Failed to connect to transcription service"}))
                return

            logger.info("Connected to Deepgram")

            # Process audio from queue
            try:
                while True:
                    chunk = await audio_queue.get()
                    if chunk is None:
                        break
                    await dg_connection.send(chunk)
            except Exception as e:
                logger.error(f"Error sending audio to Deepgram: {e}")
            finally:
                await dg_connection.finish()
                logger.info("Deepgram connection finished")

        except Exception as e:
            logger.error(f"Deepgram Service Error: {e}")
            # Only try to send error if websocket is likely still open
            try:
                await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
            except:
                pass

deepgram_service = DeepgramService()
