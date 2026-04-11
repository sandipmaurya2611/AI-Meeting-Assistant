from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Meeting
from pydantic import BaseModel
from typing import List, Optional
import uuid
import secrets

router = APIRouter()

class MeetingCreate(BaseModel):
    host_id: str
    title: str
    room_name: Optional[str] = None  # Auto-generate if not provided

class MeetingResponse(BaseModel):
    id: str
    title: str
    room_name: str
    host_id: str
    meeting_url: str
    
    class Config:
        from_attributes = True

class ParticipantJoin(BaseModel):
    user_id: str
    username: str

@router.post("/", response_model=MeetingResponse)
async def create_meeting(meeting_in: MeetingCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new meeting room.
    
    Returns a meeting with a shareable URL that others can use to join.
    """
    # Auto-generate room name if not provided
    room_name = meeting_in.room_name or f"room-{secrets.token_urlsafe(8)}"
    
    new_meeting = Meeting(
        host_id=meeting_in.host_id,
        title=meeting_in.title,
        room_name=room_name
    )
    db.add(new_meeting)
    await db.commit()
    await db.refresh(new_meeting)
    
    # Generate shareable meeting URL
    meeting_url = f"http://localhost:3000/join/{room_name}"
    
    return MeetingResponse(
        id=str(new_meeting.id),
        title=new_meeting.title,
        room_name=new_meeting.room_name,
        host_id=str(new_meeting.host_id),
        meeting_url=meeting_url
    )

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: str, db: AsyncSession = Depends(get_db)):
    """Get meeting details by ID."""
    result = await db.execute(
        select(Meeting).where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    meeting_url = f"http://localhost:3000/join/{meeting.room_name}"
    
    return MeetingResponse(
        id=str(meeting.id),
        title=meeting.title,
        room_name=meeting.room_name,
        host_id=str(meeting.host_id),
        meeting_url=meeting_url
    )

@router.get("/room/{room_name}", response_model=MeetingResponse)
async def get_meeting_by_room(room_name: str, db: AsyncSession = Depends(get_db)):
    """Get meeting details by room name (for joining via shareable link)."""
    result = await db.execute(
        select(Meeting).where(Meeting.room_name == room_name)
    )
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting room not found")
    
    meeting_url = f"http://localhost:3000/join/{meeting.room_name}"
    
    return MeetingResponse(
        id=str(meeting.id),
        title=meeting.title,
        room_name=meeting.room_name,
        host_id=str(meeting.host_id),
        meeting_url=meeting_url
    )

@router.get("/")
async def list_meetings(db: AsyncSession = Depends(get_db)):
    """List all meetings."""
    result = await db.execute(select(Meeting))
    meetings = result.scalars().all()
    
    return [
        MeetingResponse(
            id=str(m.id),
            title=m.title,
            room_name=m.room_name,
            host_id=str(m.host_id),
            meeting_url=f"http://localhost:3000/join/{m.room_name}"
        )
        for m in meetings
    ]

