import logging
from typing import List, Dict, Any
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGEngine:
    """Main RAG engine for retrieval and generation"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def get_relevant_context(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: The search query (e.g., transcript line)
            top_k: Number of results to return (default from settings)
        
        Returns:
            Dictionary with chunks and metadata
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        try:
            results = self.vector_store.search(query, top_k=top_k)
            
            chunks = []
            for result in results:
                chunks.append({
                    "source": result.get('source', 'unknown'),
                    "content": result.get('content', ''),
                    "score": result.get('score', 0.0),
                    "chunk_index": result.get('chunk_index', 0)
                })
            
            return {
                "query": query,
                "chunks": chunks,
                "total_results": len(chunks)
            }
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return {
                "query": query,
                "chunks": [],
                "total_results": 0,
                "error": str(e)
            }
    
    def generate_answer(
        self, 
        query: str, 
        retrieved_chunks: List[Dict[str, Any]],
        system_prompt: str = None
    ) -> str:
        """
        Generate an answer using retrieved context
        
        Args:
            query: The user's question/transcript line
            retrieved_chunks: List of relevant document chunks
            system_prompt: Optional custom system prompt
        
        Returns:
            Generated answer string
        """
        if not system_prompt:
            system_prompt = """You are a knowledgeable sales representative assistant. 
Your role is to provide accurate, factual information based ONLY on the provided context.

Rules:
1. Answer based strictly on the retrieved documents
2. If information is not in the context, say "I don't have that information in my knowledge base"
3. Be concise and professional
4. Format responses clearly with bullet points when appropriate
5. Never make up or hallucinate information
6. Cite sources when possible"""
        
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            source = chunk.get('source', 'unknown')
            content = chunk.get('content', '')
            context_parts.append(f"[Source: {source}]\n{content}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        if not context:
            return "I don't have any relevant information in my knowledge base to answer this question."
        
        # Create the prompt
        user_message = f"""Context from knowledge base:

{context}

---

Question: {query}

Please provide a clear, factual answer based on the context above."""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return f"Error generating answer: {str(e)}"
    
    def process_query(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve + generate
        
        Args:
            query: The user's question
            top_k: Number of chunks to retrieve
        
        Returns:
            Dictionary with retrieved chunks and generated answer
        """
        # Step 1: Retrieve relevant context
        context_result = self.get_relevant_context(query, top_k)
        
        # Step 2: Generate answer
        answer = self.generate_answer(query, context_result['chunks'])
        
        return {
            "query": query,
            "retrieved_chunks": context_result['chunks'],
            "answer": answer,
            "total_chunks_retrieved": context_result['total_results']
        }
