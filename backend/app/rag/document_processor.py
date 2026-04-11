import logging
from typing import List, Dict, Any
from pathlib import Path
import tiktoken
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

class DocumentLoader:
    """Load documents from various file formats"""
    
    def __init__(self):
        self.supported_extensions = {'.txt', '.pdf', '.docx', '.md'}
    
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """Load a single file and return its content with metadata"""
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        extension = path.suffix.lower()
        
        try:
            if extension == '.txt' or extension == '.md':
                content = self._load_text(file_path)
            elif extension == '.pdf':
                content = self._load_pdf(file_path)
            elif extension == '.docx':
                content = self._load_docx(file_path)
            else:
                logger.warning(f"Unsupported file type: {extension}")
                return None
            
            return {
                'content': content,
                'metadata': {
                    'source': path.name,
                    'file_path': str(path),
                    'file_type': extension,
                    'file_size': path.stat().st_size
                }
            }
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return None
    
    def _load_text(self, file_path: str) -> str:
        """Load plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_pdf(self, file_path: str) -> str:
        """Load PDF file"""
        reader = PdfReader(file_path)
        text = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text.append(f"[Page {i+1}]\n{page_text}")
        return "\n\n".join(text)
    
    def _load_docx(self, file_path: str) -> str:
        """Load DOCX file"""
        doc = DocxDocument(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    def load_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Load all supported documents from a directory"""
        documents = []
        path = Path(directory_path)
        
        if not path.exists():
            logger.error(f"Directory not found: {directory_path}")
            return documents
        
        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                doc = self.load_file(str(file_path))
                if doc:
                    documents.append(doc)
        
        logger.info(f"Loaded {len(documents)} documents from {directory_path}")
        return documents


class DocumentChunker:
    """Split documents into chunks with token counting"""
    
    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Use a simple tokenizer since we don't need OpenAI's specific one anymore
        # but tiktoken is still good for general purpose token counting
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_tokens = self.count_tokens(para)
            
            # If single paragraph exceeds chunk size, split it
            if para_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append({
                        'content': '\n\n'.join(current_chunk),
                        'metadata': metadata.copy(),
                        'tokens': current_tokens
                    })
                    current_chunk = []
                    current_tokens = 0
                
                # Split long paragraph by sentences
                sentences = para.split('. ')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    sent_tokens = self.count_tokens(sentence)
                    
                    if current_tokens + sent_tokens > self.chunk_size:
                        if current_chunk:
                            chunks.append({
                                'content': '\n\n'.join(current_chunk),
                                'metadata': metadata.copy(),
                                'tokens': current_tokens
                            })
                        current_chunk = [sentence]
                        current_tokens = sent_tokens
                    else:
                        current_chunk.append(sentence)
                        current_tokens += sent_tokens
            
            # Normal paragraph processing
            elif current_tokens + para_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append({
                        'content': '\n\n'.join(current_chunk),
                        'metadata': metadata.copy(),
                        'tokens': current_tokens
                    })
                current_chunk = [para]
                current_tokens = para_tokens
            else:
                current_chunk.append(para)
                current_tokens += para_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                'content': '\n\n'.join(current_chunk),
                'metadata': metadata.copy(),
                'tokens': current_tokens
            })
        
        # Add chunk index to metadata
        for i, chunk in enumerate(chunks):
            chunk['metadata']['chunk_index'] = i
            chunk['metadata']['total_chunks'] = len(chunks)
        
        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chunk multiple documents"""
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_text(doc['content'], doc['metadata'])
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
