import logging
from pathlib import Path
from typing import List, Dict, Any
from app.core.config import settings
from app.rag.document_processor import DocumentLoader, DocumentChunker
from app.rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Handle document indexing pipeline"""
    
    def __init__(self):
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.vector_store = get_vector_store()
    
    def index_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Index all documents in a directory
        
        Returns:
            Statistics about the indexing process
        """
        logger.info(f"Starting indexing of directory: {directory_path}")
        
        # Load documents
        documents = self.loader.load_directory(directory_path)
        
        if not documents:
            logger.warning(f"No documents found in {directory_path}")
            return {
                "success": False,
                "documents_loaded": 0,
                "chunks_created": 0,
                "error": "No documents found"
            }
        
        # Chunk documents
        chunks = self.chunker.chunk_documents(documents)
        
        # Add to vector store
        success = self.vector_store.add_documents(chunks)
        
        stats = {
            "success": success,
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "directory": directory_path
        }
        
        logger.info(f"Indexing complete: {stats}")
        return stats
    
    def index_all_folders(self) -> Dict[str, Any]:
        """
        Index all document folders
        
        Returns:
            Combined statistics
        """
        base_path = Path(settings.DOCUMENTS_PATH)
        
        folders = [
            "job_descriptions",
            "emails",
            "meeting_notes",
            "crm_records",
            "pdfs"
        ]
        
        total_stats = {
            "success": True,
            "total_documents": 0,
            "total_chunks": 0,
            "folders_indexed": [],
            "errors": []
        }
        
        for folder in folders:
            folder_path = base_path / folder
            
            if not folder_path.exists():
                logger.warning(f"Folder not found: {folder_path}")
                folder_path.mkdir(parents=True, exist_ok=True)
                continue
            
            try:
                stats = self.index_directory(str(folder_path))
                
                if stats['success']:
                    total_stats['total_documents'] += stats['documents_loaded']
                    total_stats['total_chunks'] += stats['chunks_created']
                    total_stats['folders_indexed'].append({
                        "folder": folder,
                        "documents": stats['documents_loaded'],
                        "chunks": stats['chunks_created']
                    })
                else:
                    total_stats['errors'].append({
                        "folder": folder,
                        "error": stats.get('error', 'Unknown error')
                    })
            except Exception as e:
                logger.error(f"Error indexing {folder}: {str(e)}")
                total_stats['errors'].append({
                    "folder": folder,
                    "error": str(e)
                })
                total_stats['success'] = False
        
        return total_stats
    
    def add_document(self, file_path: str) -> Dict[str, Any]:
        """
        Add a single document to the index
        
        Args:
            file_path: Path to the document file
        
        Returns:
            Statistics about the indexing
        """
        logger.info(f"Indexing single document: {file_path}")
        
        # Load document
        doc = self.loader.load_file(file_path)
        
        if not doc:
            return {
                "success": False,
                "error": "Failed to load document"
            }
        
        # Chunk document
        chunks = self.chunker.chunk_text(doc['content'], doc['metadata'])
        
        # Add to vector store
        success = self.vector_store.add_documents(chunks)
        
        return {
            "success": success,
            "file": file_path,
            "chunks_created": len(chunks)
        }
    
    def clear_index(self) -> bool:
        """Clear all documents from the index"""
        logger.info("Clearing document index")
        return self.vector_store.delete_all()
