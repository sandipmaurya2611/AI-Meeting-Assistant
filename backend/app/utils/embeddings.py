import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from app.core.config import settings

# Ensure index directory exists
os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)

# Global embedding model
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model

def get_embedding(text: str) -> List[float]:
    model = get_model()
    return model.encode(text).tolist()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Simple character-based chunking. For better results use token-based."""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def _get_index_path(meeting_id: str) -> str:
    return os.path.join(settings.FAISS_INDEX_DIR, f"{meeting_id}.index")

def _get_mapping_path(meeting_id: str) -> str:
    return os.path.join(settings.FAISS_INDEX_DIR, f"{meeting_id}.json")

def build_or_update_index(meeting_id: str, texts: List[str], metadata_list: List[Dict[str, Any]]):
    """
    Add new texts to the FAISS index for a meeting.
    This is a simplified append-only approach.
    """
    if not texts:
        return

    # Generate embeddings
    embeddings = []
    for txt in texts:
        embeddings.append(get_embedding(txt))
    
    embeddings_np = np.array(embeddings).astype('float32')
    
    index_path = _get_index_path(meeting_id)
    mapping_path = _get_mapping_path(meeting_id)
    
    # Load existing or create new
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
        with open(mapping_path, 'r') as f:
            mapping = json.load(f)
    else:
        dimension = len(embeddings[0])
        index = faiss.IndexFlatL2(dimension)
        mapping = {}

    # Add to index
    start_id = index.ntotal
    index.add(embeddings_np)
    
    # Update mapping
    for i, meta in enumerate(metadata_list):
        mapping[str(start_id + i)] = meta
        
    # Save
    faiss.write_index(index, index_path)
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f)

def search_similar(meeting_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
    index_path = _get_index_path(meeting_id)
    mapping_path = _get_mapping_path(meeting_id)
    
    if not os.path.exists(index_path):
        return []
        
    index = faiss.read_index(index_path)
    with open(mapping_path, 'r') as f:
        mapping = json.load(f)
        
    query_vec = np.array([get_embedding(query)]).astype('float32')
    distances, indices = index.search(query_vec, k)
    
    results = []
    for i in range(k):
        idx = str(indices[0][i])
        if idx in mapping:
            item = mapping[idx]
            item['score'] = float(distances[0][i])
            results.append(item)
            
    return results
