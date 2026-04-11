from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    meetings = relationship("Meeting", back_populates="host")

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    host_id = Column(String, ForeignKey("users.id"))
    title = Column(String)
    room_name = Column(String)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    recording_url = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    
    host = relationship("User", back_populates="meetings")
    transcripts = relationship("Transcript", back_populates="meeting")
    suggestions = relationship("Suggestion", back_populates="meeting")

class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, ForeignKey("meetings.id"))
    ts = Column(DateTime(timezone=True), server_default=func.now())
    speaker = Column(String, nullable=True)
    text = Column(Text)
    
    meeting = relationship("Meeting", back_populates="transcripts")

class Suggestion(Base):
    __tablename__ = "suggestions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    meeting_id = Column(String, ForeignKey("meetings.id"))
    ts = Column(DateTime(timezone=True), server_default=func.now())
    text = Column(Text)
    accepted = Column(Boolean, default=False)
    
    meeting = relationship("Meeting", back_populates="suggestions")
