from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
import numpy as np
import os
import json
import faiss
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global embedding model instance to avoid reloading
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedding_model

class VectorStore(ABC):
    """Abstract base class for vector stores"""
    
    @abstractmethod
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add document chunks to the vector store"""
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def delete_all(self) -> bool:
        """Clear all documents from the store"""
        pass


class FAISSVectorStore(VectorStore):
    """FAISS-based vector store"""
    
    def __init__(self):
        self.faiss = faiss
        self.index_path = os.path.join(settings.FAISS_INDEX_DIR, "rag_index.faiss")
        self.metadata_path = os.path.join(settings.FAISS_INDEX_DIR, "rag_metadata.json")
        self.dimension = settings.EMBEDDING_DIM
        self.model = get_embedding_model()
        
        os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)
        
        # Load or create index
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                # Only load if metadata file is not empty
                if os.path.getsize(self.metadata_path) > 0:
                    self.index = faiss.read_index(self.index_path)
                    with open(self.metadata_path, 'r') as f:
                        self.metadata = json.load(f)
                    logger.info(f"Loaded existing FAISS index with {len(self.metadata)} documents")
                else:
                    raise ValueError("Metadata file is empty")
            except Exception as e:
                logger.warning(f"Failed to load existing index ({e}). Creating new one.")
                self.index = faiss.IndexFlatL2(self.dimension)
                self.metadata = []
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from local model"""
        return self.model.encode(text).tolist()
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add chunks to FAISS index"""
        try:
            embeddings = []
            new_metadata = []
            
            for chunk in chunks:
                embedding = self._get_embedding(chunk['content'])
                embeddings.append(embedding)
                new_metadata.append({
                    'content': chunk['content'],
                    'source': chunk['metadata'].get('source', 'unknown'),
                    'file_path': chunk['metadata'].get('file_path', ''),
                    'chunk_index': chunk['metadata'].get('chunk_index', 0),
                    'tokens': chunk.get('tokens', 0)
                })
            
            if not embeddings:
                return True
                
            embeddings_np = np.array(embeddings).astype('float32')
            self.index.add(embeddings_np)
            self.metadata.extend(new_metadata)
            
            # Save index and metadata
            self.faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'w') as f:
                json.dump(self.metadata, f)
            
            logger.info(f"Added {len(chunks)} chunks to FAISS index")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to FAISS: {str(e)}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search FAISS index"""
        try:
            if self.index.ntotal == 0:
                return []
                
            query_embedding = self._get_embedding(query)
            query_vec = np.array([query_embedding]).astype('float32')
            
            distances, indices = self.index.search(query_vec, min(top_k, self.index.ntotal))
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result['score'] = float(distances[0][i])
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error searching FAISS: {str(e)}")
            return []
    
    def delete_all(self) -> bool:
        """Clear FAISS index"""
        try:
            import os
            self.index = self.faiss.IndexFlatL2(self.dimension)
            self.metadata = []
            
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            
            logger.info("Cleared FAISS index")
            return True
        except Exception as e:
            logger.error(f"Error clearing FAISS: {str(e)}")
            return False


class PineconeVectorStore(VectorStore):
    """Pinecone-based vector store"""
    
    def __init__(self):
        from pinecone import Pinecone, ServerlessSpec
        
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.model = get_embedding_model()
        
        # Create index if it doesn't exist
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=settings.EMBEDDING_DIM,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=settings.PINECONE_ENVIRONMENT
                )
            )
        
        self.index = self.pc.Index(self.index_name)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from local model"""
        return self.model.encode(text).tolist()
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add chunks to Pinecone"""
        try:
            vectors = []
            for i, chunk in enumerate(chunks):
                embedding = self._get_embedding(chunk['content'])
                vectors.append({
                    'id': f"chunk_{i}_{hash(chunk['content'])}",
                    'values': embedding,
                    'metadata': {
                        'content': chunk['content'][:1000],  # Pinecone metadata limit
                        'source': chunk['metadata'].get('source', 'unknown'),
                        'file_path': chunk['metadata'].get('file_path', ''),
                        'chunk_index': chunk['metadata'].get('chunk_index', 0),
                        'tokens': chunk.get('tokens', 0)
                    }
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Added {len(chunks)} chunks to Pinecone")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to Pinecone: {str(e)}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search Pinecone index"""
        try:
            query_embedding = self._get_embedding(query)
            
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            formatted_results = []
            for match in results['matches']:
                formatted_results.append({
                    'content': match['metadata'].get('content', ''),
                    'source': match['metadata'].get('source', 'unknown'),
                    'file_path': match['metadata'].get('file_path', ''),
                    'chunk_index': match['metadata'].get('chunk_index', 0),
                    'score': match['score']
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching Pinecone: {str(e)}")
            return []
    
    def delete_all(self) -> bool:
        """Clear Pinecone index"""
        try:
            self.index.delete(delete_all=True)
            logger.info("Cleared Pinecone index")
            return True
        except Exception as e:
            logger.error(f"Error clearing Pinecone: {str(e)}")
            return False


class PgVectorStore(VectorStore):
    """PostgreSQL with pgvector extension"""
    
    def __init__(self):
        import psycopg2
        
        self.conn = psycopg2.connect(settings.DATABASE_URL.replace('sqlite+aiosqlite', 'postgresql'))
        self.model = get_embedding_model()
        self._setup_table()
    
    def _setup_table(self):
        """Create vector table if not exists"""
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector({settings.EMBEDDING_DIM}),
                    source TEXT,
                    file_path TEXT,
                    chunk_index INTEGER,
                    tokens INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS embedding_idx 
                ON document_embeddings 
                USING ivfflat (embedding vector_cosine_ops)
            """)
        self.conn.commit()
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from local model"""
        return self.model.encode(text).tolist()
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> bool:
        """Add chunks to pgvector"""
        try:
            from psycopg2.extras import execute_values
            
            data = []
            for chunk in chunks:
                embedding = self._get_embedding(chunk['content'])
                data.append((
                    chunk['content'],
                    embedding,
                    chunk['metadata'].get('source', 'unknown'),
                    chunk['metadata'].get('file_path', ''),
                    chunk['metadata'].get('chunk_index', 0),
                    chunk.get('tokens', 0)
                ))
            
            with self.conn.cursor() as cur:
                execute_values(
                    cur,
                    """
                    INSERT INTO document_embeddings 
                    (content, embedding, source, file_path, chunk_index, tokens)
                    VALUES %s
                    """,
                    data
                )
            self.conn.commit()
            
            logger.info(f"Added {len(chunks)} chunks to pgvector")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to pgvector: {str(e)}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search pgvector"""
        try:
            query_embedding = self._get_embedding(query)
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT content, source, file_path, chunk_index, tokens,
                           1 - (embedding <=> %s::vector) as score
                    FROM document_embeddings
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding, query_embedding, top_k))
                
                results = []
                for row in cur.fetchall():
                    results.append({
                        'content': row[0],
                        'source': row[1],
                        'file_path': row[2],
                        'chunk_index': row[3],
                        'tokens': row[4],
                        'score': float(row[5])
                    })
                
                return results
        except Exception as e:
            logger.error(f"Error searching pgvector: {str(e)}")
            return []
    
    def delete_all(self) -> bool:
        """Clear pgvector table"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE document_embeddings")
            self.conn.commit()
            logger.info("Cleared pgvector table")
            return True
        except Exception as e:
            logger.error(f"Error clearing pgvector: {str(e)}")
            return False


def get_vector_store() -> VectorStore:
    """Factory function to get the configured vector store"""
    db_type = settings.VECTOR_DB_TYPE.lower()
    
    if db_type == "pinecone":
        return PineconeVectorStore()
    elif db_type == "pgvector":
        return PgVectorStore()
    else:  # default to FAISS
        return FAISSVectorStore()
