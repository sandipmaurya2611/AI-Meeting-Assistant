import sys
sys.path.insert(0, 'D:\\Ai meeting Assistant\\backend')

from app.rag.document_processor import DocumentLoader, DocumentChunker
from app.core.config import settings
from pathlib import Path

print("Testing Document Loading...")
print(f"Documents path: {settings.DOCUMENTS_PATH}")
print()

loader = DocumentLoader()

# Test loading from pdfs folder
pdfs_path = Path(settings.DOCUMENTS_PATH) / "pdfs"
print(f"Checking: {pdfs_path}")
print(f"Exists: {pdfs_path.exists()}")

if pdfs_path.exists():
    files = list(pdfs_path.glob("*"))
    print(f"Files found: {len(files)}")
    for f in files:
        print(f"  - {f.name}")
    
    print("\nLoading documents...")
    docs = loader.load_directory(str(pdfs_path))
    print(f"Loaded: {len(docs)} documents")
    
    if docs:
        print("\nFirst document:")
        print(f"  Source: {docs[0]['metadata']['source']}")
        print(f"  Content length: {len(docs[0]['content'])} chars")
        print(f"  Content preview: {docs[0]['content'][:200]}...")
        
        # Test chunking
        print("\nTesting chunking...")
        chunker = DocumentChunker(chunk_size=300, chunk_overlap=50)
        chunks = chunker.chunk_documents(docs)
        print(f"Created {len(chunks)} chunks")
        
        if chunks:
            print("\nFirst chunk:")
            print(f"  Tokens: {chunks[0]['tokens']}")
            print(f"  Content: {chunks[0]['content'][:200]}...")
