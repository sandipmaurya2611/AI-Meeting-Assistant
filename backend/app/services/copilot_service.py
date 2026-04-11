import logging
import re
from typing import Dict, Any, List
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)


class CopilotResponse:
    """Structured copilot response"""
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.suggestion = self._extract_field("Suggestion", raw_text)
        self.follow_up_question = self._extract_field("FollowUpQuestion", raw_text)
        self.confusion_detected = self._extract_field("ConfusionDetected", raw_text)
        self.talking_points = self._extract_talking_points(raw_text)
        self.crm_update = self._extract_field("CRM_Update", raw_text)
        self.task_creation = self._extract_field("TaskCreation", raw_text)
    
    def _extract_field(self, field_name: str, text: str) -> str:
        """Extract a single field from the response"""
        pattern = rf"{field_name}:\s*(.+?)(?:\n(?:[A-Z])|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            value = match.group(1).strip()
            # Remove multiple whitespace
            value = re.sub(r'\s+', ' ', value)
            return value if value and value.lower() != "none" else ""
        return ""
    
    def _extract_talking_points(self, text: str) -> List[str]:
        """Extract talking points as a list"""
        points = []
        pattern = r"TalkingPoints:\s*(.+?)(?:\n(?:[A-Z])|$)"
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            points_text = match.group(1)
            # Find all bullet points
            bullets = re.findall(r'-\s*(.+?)(?:\n|$)', points_text)
            for bullet in bullets:
                bullet = bullet.strip()
                if bullet and bullet.lower() != "none":
                    points.append(bullet)
        
        return points if points else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "suggestion": self.suggestion,
            "follow_up_question": self.follow_up_question,
            "confusion_detected": self.confusion_detected.lower() == "yes" if self.confusion_detected else False,
            "talking_points": self.talking_points,
            "crm_update": self.crm_update,
            "task_creation": self.task_creation,
            "raw_response": self.raw_text
        }


class MeetingCopilot:
    """Real-Time AI Meeting Co-Pilot"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.system_prompt = """You are a Real-Time AI Meeting Co-Pilot.

Your goals:
1. Understand what the client just said (Transcript).
2. Understand the overall meeting situation (Context).
3. Use ONLY the internal knowledge provided by the RAG results (Relevant Documents).
4. Suggest the BEST possible next sentence the user should say (maximum 20 words).
5. Maintain confidence, clarity, and a helpful tone.
6. Detect any confusion from the client and flag it.
7. Suggest highly relevant follow-up questions.
8. Generate concise bullet-point talking points.
9. Suggest task creation (follow-up, sending documents, scheduling a demo) if needed.
10. NO hallucination — strictly use information from transcript, context, or RAG documents.

You MUST respond in this exact format:

Suggestion: <Best next sentence the user should say, <= 20 words only>

FollowUpQuestion: <One helpful follow-up question to ask OR "None">

ConfusionDetected: <Yes or No — Is the client confused?>

TalkingPoints:
- <Bullet point 1 summarizing key helpful points OR "None">
- <Bullet point 2 OR "None">
- <Bullet point 3 OR "None">

CRM_Update:
<One single CRM update suggestion based on the conversation OR "None">

TaskCreation:
<One task to create (example: send pricing PDF, schedule demo, send proposal) OR "None">

Rules:
- DO NOT invent information that is not present in the RAG results or context.
- Always stay short, confident, clear, and helpful.
- If any item is not needed, respond with "None"."""
    
    def build_copilot_prompt(
        self,
        transcript: str,
        context: Dict[str, Any],
        rag_results: List[Dict[str, Any]]
    ) -> str:
        """Build the copilot prompt with all context"""
        
        # Format context
        context_text = "No context available"
        if context:
            context_parts = []
            if context.get("topic"):
                context_parts.append(f"Topic: {context['topic']}")
            if context.get("last_history"):
                history = context["last_history"]
                history_text = "\n".join([f"  - [{h.get('speaker', 'Unknown')}]: {h.get('text', '')}" for h in history[-3:]])
                context_parts.append(f"Recent conversation:\n{history_text}")
            if context.get("action_items"):
                context_parts.append(f"Action items: {len(context['action_items'])} pending")
            
            context_text = "\n".join(context_parts) if context_parts else "No context available"
        
        # Format RAG results
        rag_text = "No relevant documents found"
        if rag_results:
            rag_parts = []
            for i, result in enumerate(rag_results[:3], 1):
                source = result.get('source', 'Unknown')
                content = result.get('content', '')[:300]  # Limit content length
                rag_parts.append(f"{i}. [Source: {source}]\n   {content}...")
            rag_text = "\n\n".join(rag_parts)
        
        # Build final prompt
        user_prompt = f"""Here is your input:

Transcript:
{transcript}

Context:
{context_text}

Relevant Documents (RAG Results):
{rag_text}

Now produce your output STRICTLY in the required structured format."""
        
        return user_prompt
    
    def get_copilot_suggestion(
        self,
        transcript: str,
        context: Dict[str, Any] = None,
        rag_results: List[Dict[str, Any]] = None
    ) -> CopilotResponse:
        """
        Get structured copilot suggestions
        
        Args:
            transcript: What the client just said
            context: Meeting context (optional)
            rag_results: Relevant documents from RAG search (optional)
        
        Returns:
            CopilotResponse with structured suggestions
        """
        try:
            user_prompt = self.build_copilot_prompt(
                transcript=transcript,
                context=context or {},
                rag_results=rag_results or []
            )
            
            logger.info("Generating copilot suggestions...")
            
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower for more consistent structured output
                max_tokens=600
            )
            
            raw_response = response.choices[0].message.content
            logger.info("Copilot response generated successfully")
            
            return CopilotResponse(raw_response)
            
        except Exception as e:
            logger.error(f"Error generating copilot suggestions: {str(e)}")
            # Return empty response on error
            return CopilotResponse("Suggestion: None\nFollowUpQuestion: None\nConfusionDetected: No\nTalkingPoints:\n- None\nCRM_Update: None\nTaskCreation: None")
