from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Transcript
from app.core.database import SessionLocal as async_session_factory
import uuid
import logging

logger = logging.getLogger(__name__)

async def save_transcript(meeting_id: str, speaker: str, text: str, timestamp):
    """
    Saves a transcript segment to the database.
    """
    try:
        async with async_session_factory() as session:
            # Ensure meeting_id is a valid UUID
            try:
                meeting_uuid = uuid.UUID(meeting_id)
            except ValueError:
                logger.warning(f"Invalid meeting_id: {meeting_id}")
                return

            transcript = Transcript(
                meeting_id=meeting_uuid,
                speaker=speaker,
                text=text,
                ts=timestamp
            )
            session.add(transcript)
            await session.commit()
            logger.info(f"Saved transcript for meeting {meeting_id}")
    except Exception as e:
        logger.error(f"Failed to save transcript: {e}")
