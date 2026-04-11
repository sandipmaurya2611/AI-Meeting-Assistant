import sys
sys.path.insert(0, 'D:\\Ai meeting Assistant\\backend')

from app.rag.document_processor import DocumentLoader, DocumentChunker
from app.rag.vector_store import get_vector_store
from app.core.config import settings
from pathlib import Path

print("Testing RAG System End-to-End...")
print(f"Vector DB Type: {settings.VECTOR_DB_TYPE}")
print(f"OpenAI API Key: {'Set' if settings.OPENAI_API_KEY else 'Not Set'}")
print()

# Step 1: Load documents
print("Step 1: Loading documents...")
loader = DocumentLoader()
pdfs_path = Path(settings.DOCUMENTS_PATH) / "pdfs"
docs = loader.load_directory(str(pdfs_path))
print(f"✓ Loaded {len(docs)} documents")

# Step 2: Chunk documents
print("\nStep 2: Chunking documents...")
chunker = DocumentChunker(chunk_size=300, chunk_overlap=50)
chunks = chunker.chunk_documents(docs)
print(f"✓ Created {len(chunks)} chunks")

# Step 3: Initialize vector store
print("\nStep 3: Initializing vector store...")
try:
    vector_store = get_vector_store()
    print(f"✓ Vector store initialized: {type(vector_store).__name__}")
except Exception as e:
    print(f"✗ Error: {str(e)}")
    sys.exit(1)

# Step 4: Add documents to vector store
print("\nStep 4: Adding documents to vector store...")
try:
    success = vector_store.add_documents(chunks[:3])  # Test with first 3 chunks
    if success:
        print(f"✓ Successfully added 3 test chunks")
    else:
        print("✗ Failed to add documents")
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test search
print("\nStep 5: Testing search...")
try:
    query = "What is the pricing for standard plan?"
    results = vector_store.search(query, top_k=2)
    print(f"✓ Search returned {len(results)} results")
    
    if results:
        print("\nTop result:")
        print(f"  Source: {results[0].get('source')}")
        print(f"  Score: {results[0].get('score')}")
        print(f"  Content: {results[0].get('content')[:150]}...")
except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test completed!")
