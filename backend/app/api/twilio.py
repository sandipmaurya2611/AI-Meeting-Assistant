from fastapi import APIRouter, HTTPException
from app.core.config import settings
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

router = APIRouter()

@router.get("/token")
async def get_twilio_token(room: str, identity: str):
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY_SID, settings.TWILIO_API_KEY_SECRET]):
        raise HTTPException(status_code=500, detail="Twilio credentials missing")

    token = AccessToken(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_API_KEY_SID,
        settings.TWILIO_API_KEY_SECRET,
        identity=identity
    )

    video_grant = VideoGrant(room=room)
    token.add_grant(video_grant)

    return {"token": token.to_jwt(), "room": room}
