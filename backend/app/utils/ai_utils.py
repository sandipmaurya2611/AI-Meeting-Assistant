from typing import List, Dict, Any
from app.core.config import settings
from app.utils.embeddings import search_similar

def build_prompt(context: Dict, message: str, retrieved_chunks: List[Dict] = None) -> str:
    topic = context.get("topic") or "(unknown)"
    history = context.get("last_history") or []
    history_text = "\n".join([f"[{h['speaker']}] {h['text']}" for h in history])
    
    retrieved_text = ""
    if retrieved_chunks:
        retrieved_text = "\nRelevant past context:\n" + "\n".join([f"- {c['text']} (Speaker: {c.get('speaker', 'Unknown')})" for c in retrieved_chunks]) + "\n"

    prompt = f"""You are an AI meeting co-pilot.
Meeting topic: {topic}

{retrieved_text}
Recent transcript:
{history_text}

Action items: {context.get('action_items')}
Recent sentiments: {context.get('recent_sentiments')}
Recent intents: {context.get('recent_intents')}

User message: {message}

Respond with:
- concise meeting summary (2-3 lines)
- list of action items detected (title, owner if present)
- any follow-up questions the AI should ask
- tone-aware note if client seems upset
"""
    return prompt

def call_ai(prompt: str) -> str:
    """Call Groq API to get AI-powered meeting insights."""
    if not settings.GROQ_API_KEY:
        return "[ERROR] GROQ_API_KEY not found in environment variables."
    
    try:
        from groq import Groq
        client = Groq(api_key=settings.GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are an AI meeting co-pilot assistant. Provide concise, actionable insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR] Failed to call Groq API: {str(e)}"

def rag_ask(meeting_id: str, message: str, context_store) -> str:
    # 1. Get short context from Redis
    ctx = context_store.get_context(meeting_id, last_n=15)
    
    # 2. Search FAISS for relevant chunks
    retrieved = search_similar(meeting_id, message, k=5)
    
    # 3. Build prompt
    prompt = build_prompt(ctx, message, retrieved_chunks=retrieved)
    
    # 4. Call AI
    return call_ai(prompt)
