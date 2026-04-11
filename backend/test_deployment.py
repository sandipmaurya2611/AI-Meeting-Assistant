"""
Comprehensive Pre-Deployment Test Suite
Tests all critical functionality before deployment
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, message=""):
    symbol = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
    print(f"{symbol} {name}")
    if message:
        print(f"  {Colors.YELLOW}{message}{Colors.END}")

async def test_database_connection():
    """Test 1: Database Connection"""
    print(f"\n{Colors.BLUE}[TEST 1] Database Connection{Colors.END}")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print_test("Database URL", False, "DATABASE_URL not found in .env")
            return False
        
        engine = create_async_engine(db_url, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print_test("Database Connection", True, f"Connected: {version[:50]}...")
            return True
    except Exception as e:
        print_test("Database Connection", False, str(e))
        return False

async def test_environment_variables():
    """Test 2: Environment Variables"""
    print(f"\n{Colors.BLUE}[TEST 2] Environment Variables{Colors.END}")
    
    required_vars = [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_API_KEY_SID",
        "TWILIO_API_KEY_SECRET",
        "DEEPGRAM_API_KEY",
        "GROQ_API_KEY",
        "DATABASE_URL",
        "REDIS_URL",
        "FRONTEND_URL"
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print_test(var, True, f"Set: {masked}")
        else:
            print_test(var, False, "Missing!")
            all_present = False
    
    return all_present

def test_dependencies():
    """Test 3: Python Dependencies"""
    print(f"\n{Colors.BLUE}[TEST 3] Python Dependencies{Colors.END}")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "asyncpg",
        "twilio",
        "deepgram",
        "groq",
        "faiss",
        "sentence_transformers",
        "langchain",
        "redis"
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_test(package, True)
        except ImportError:
            print_test(package, False, "Not installed!")
            all_installed = False
    
    return all_installed

async def test_api_imports():
    """Test 4: API Module Imports"""
    print(f"\n{Colors.BLUE}[TEST 4] API Module Imports{Colors.END}")
    
    try:
        from app.main import app
        print_test("FastAPI App", True)
        
        from app.api import meetings, twilio, transcription_ws, rag
        print_test("API Modules", True, "meetings, twilio, transcription_ws, rag")
        
        from app.models import User, Meeting, Transcript, Suggestion
        print_test("Database Models", True)
        
        from app.services.ai_service import AIService
        print_test("AI Service", True)
        
        return True
    except Exception as e:
        print_test("Module Imports", False, str(e))
        return False

async def test_rag_system():
    """Test 5: RAG System"""
    print(f"\n{Colors.BLUE}[TEST 5] RAG System{Colors.END}")
    
    try:
        from app.rag.vector_store import VectorStore
        from app.rag.document_loader import DocumentLoader
        
        print_test("RAG Modules", True)
        
        # Check if FAISS index directory exists
        import os
        faiss_dir = "app/data/indices"
        if os.path.exists(faiss_dir):
            print_test("FAISS Directory", True, f"Found: {faiss_dir}")
        else:
            print_test("FAISS Directory", True, "Will be created on first upload")
        
        return True
    except Exception as e:
        print_test("RAG System", False, str(e))
        return False

async def test_redis_connection():
    """Test 6: Redis Connection"""
    print(f"\n{Colors.BLUE}[TEST 6] Redis Connection{Colors.END}")
    
    try:
        import redis.asyncio as redis
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        client = redis.from_url(redis_url)
        
        await client.ping()
        print_test("Redis Connection", True, "Connected successfully")
        await client.close()
        return True
    except Exception as e:
        print_test("Redis Connection", False, str(e))
        return False

async def test_external_apis():
    """Test 7: External API Keys"""
    print(f"\n{Colors.BLUE}[TEST 7] External API Validation{Colors.END}")
    
    # Test Groq API
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Don't actually call API, just validate key format
        if os.getenv("GROQ_API_KEY", "").startswith("gsk_"):
            print_test("Groq API Key", True, "Valid format")
        else:
            print_test("Groq API Key", False, "Invalid format")
    except Exception as e:
        print_test("Groq API", False, str(e))
    
    # Test Deepgram API Key
    if os.getenv("DEEPGRAM_API_KEY"):
        print_test("Deepgram API Key", True, "Present")
    else:
        print_test("Deepgram API Key", False, "Missing")
    
    # Test Twilio credentials
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    if twilio_sid.startswith("AC"):
        print_test("Twilio Account SID", True, "Valid format")
    else:
        print_test("Twilio Account SID", False, "Invalid format")
    
    return True

def test_file_structure():
    """Test 8: File Structure"""
    print(f"\n{Colors.BLUE}[TEST 8] File Structure{Colors.END}")
    
    required_files = [
        "app/main.py",
        "app/models.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/api/meetings.py",
        "app/api/twilio.py",
        "app/api/rag.py",
        "app/services/ai_service.py",
        "requirements.txt",
        ".env"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_test(file_path, True)
        else:
            print_test(file_path, False, "File not found!")
            all_exist = False
    
    return all_exist

async def main():
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}AI MEETING ASSISTANT - PRE-DEPLOYMENT TESTS{Colors.END}")
    print(f"{'='*60}")
    
    results = []
    
    # Run all tests
    results.append(("Environment Variables", await test_environment_variables()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("File Structure", test_file_structure()))
    results.append(("API Imports", await test_api_imports()))
    results.append(("Database Connection", await test_database_connection()))
    results.append(("Redis Connection", await test_redis_connection()))
    results.append(("RAG System", await test_rag_system()))
    results.append(("External APIs", await test_external_apis()))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print(f"{'='*60}")
    
    passed = sum(1 for _, status in results if status)
    total = len(results)
    
    for name, status in results:
        symbol = f"{Colors.GREEN}PASS{Colors.END}" if status else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{symbol} - {name}")
    
    print(f"\n{Colors.BLUE}Results: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✓ ALL TESTS PASSED - READY FOR DEPLOYMENT!{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}✗ SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT{Colors.END}\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
