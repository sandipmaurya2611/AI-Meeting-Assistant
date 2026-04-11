from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, twilio, meetings, transcription, ai_routes, rag_routes, copilot_routes, websocket_routes

app = FastAPI(title=settings.PROJECT_NAME)

# CORS - Allow frontend on both port 3000 and 5173 (Vite default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(twilio.router, prefix="/api/twilio", tags=["twilio"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["meetings"])
app.include_router(transcription.router, tags=["transcription"])
app.include_router(ai_routes.router, prefix="/api/ai", tags=["ai"])
app.include_router(rag_routes.router, prefix="/api/rag", tags=["rag"])
app.include_router(copilot_routes.router, prefix="/api/copilot", tags=["copilot"])
app.include_router(websocket_routes.router, tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "AI Meeting Assistant API"}

# Startup event to create tables (for dev simplicity, use Alembic in prod)
@app.on_event("startup")
async def startup_event():
    from app.core.database import engine, Base
    import asyncio
    from app.services.websocket_service import broadcast_ai_suggestions
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start WebSocket broadcast task
    asyncio.create_task(broadcast_ai_suggestions())
