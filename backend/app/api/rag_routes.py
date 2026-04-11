from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import logging
import os
from pathlib import Path

from app.rag.indexer import DocumentIndexer
from app.rag.rag_engine import RAGEngine
from app.rag.vector_store import get_vector_store
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize RAG components — use a SINGLE shared vector store
vector_store = get_vector_store()
rag_engine = RAGEngine(vector_store)
indexer = DocumentIndexer()
# CRITICAL: Override the indexer's vector store so indexing and search use the same instance
indexer.vector_store = vector_store


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    query: str
    top_k: Optional[int] = None


class MeetingTranscriptRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    
    transcript: str
    meeting_id: Optional[str] = "default"
    top_k: Optional[int] = None


class IndexResponse(BaseModel):
    success: bool
    message: str
    details: dict


@router.post("/index", response_model=IndexResponse)
async def index_documents(background_tasks: BackgroundTasks):
    """
    Reindex all documents from the configured folders
    
    This endpoint will:
    1. Load all documents from job_descriptions/, emails/, meeting_notes/, crm_records/, pdfs/
    2. Chunk them into optimal sizes
    3. Generate embeddings
    4. Store in the vector database
    """
    try:
        # Run indexing in background
        def run_indexing():
            stats = indexer.index_all_folders()
            logger.info(f"Indexing completed: {stats}")
        
        background_tasks.add_task(run_indexing)
        
        return IndexResponse(
            success=True,
            message="Indexing started in background",
            details={"status": "processing"}
        )
    except Exception as e:
        logger.error(f"Error starting indexing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/sync")
async def index_documents_sync():
    """
    Synchronously reindex all documents (blocks until complete)
    
    Use this for testing or when you need to wait for indexing to complete
    """
    try:
        stats = indexer.index_all_folders()
        
        return IndexResponse(
            success=stats['success'],
            message=f"Indexed {stats['total_documents']} documents into {stats['total_chunks']} chunks",
            details=stats
        )
    except Exception as e:
        logger.error(f"Error during indexing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_documents(request: SearchRequest):
    """
    Search for relevant documents based on a query
    
    Input:
    {
        "query": "They are asking about pricing",
        "top_k": 5  // optional, defaults to config value
    }
    
    Output:
    {
        "query": "...",
        "retrieved_chunks": [...],
        "answer": "...",
        "total_chunks_retrieved": 5
    }
    """
    try:
        result = rag_engine.process_query(request.query, request.top_k)
        return result
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/context-only")
async def search_context_only(request: SearchRequest):
    """
    Get only the relevant context without generating an answer
    
    Returns just the retrieved chunks in a clean format
    """
    try:
        result = rag_engine.get_relevant_context(request.query, request.top_k)
        return result
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meeting")
async def process_meeting_transcript(request: MeetingTranscriptRequest):
    """
    Process a meeting transcript line and get relevant context + answer
    
    Input:
    {
        "transcript": "User wants to know about contract renewal",
        "meeting_id": "meeting_123",  // optional
        "top_k": 5  // optional
    }
    
    Output:
    {
        "query": "...",
        "retrieved_chunks": [
            {
                "source": "contracts_notes.txt",
                "content": "...",
                "score": 0.85
            }
        ],
        "answer": "Our contracts renew automatically...",
        "total_chunks_retrieved": 5
    }
    """
    try:
        # Process the transcript through RAG
        result = rag_engine.process_query(request.transcript, request.top_k)
        
        # Add meeting_id to response
        result['meeting_id'] = request.meeting_id
        
        return result
    except Exception as e:
        logger.error(f"Error processing meeting transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    folder: str = "pdfs"
):
    """
    Upload a new document and add it to the index
    
    Args:
        file: The document file to upload
        folder: Target folder (job_descriptions, emails, meeting_notes, crm_records, pdfs)
    """
    try:
        # Validate folder
        valid_folders = ["job_descriptions", "emails", "meeting_notes", "crm_records", "pdfs"]
        if folder not in valid_folders:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid folder. Must be one of: {valid_folders}"
            )
        
        # Save file
        folder_path = Path(settings.DOCUMENTS_PATH) / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        file_path = folder_path / file.filename
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Index the document
        stats = indexer.add_document(str(file_path))
        
        return {
            "success": stats['success'],
            "message": f"Document uploaded and indexed",
            "file": file.filename,
            "chunks_created": stats.get('chunks_created', 0)
        }
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/index")
async def clear_index():
    """
    Clear all documents from the vector database
    
    WARNING: This will delete all indexed documents!
    """
    try:
        success = indexer.clear_index()
        
        return {
            "success": success,
            "message": "Index cleared successfully" if success else "Failed to clear index"
        }
    except Exception as e:
        logger.error(f"Error clearing index: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """
    Get statistics about the indexed documents
    """
    try:
        # This is a simple implementation - you can extend it based on your vector store
        return {
            "vector_db_type": settings.VECTOR_DB_TYPE,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "top_k_default": settings.TOP_K_RESULTS,
            "documents_path": settings.DOCUMENTS_PATH
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
