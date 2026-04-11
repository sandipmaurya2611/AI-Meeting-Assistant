"""
Simple startup script for the backend server.
This script starts the FastAPI server with proper error handling.
"""

import sys
import subprocess

def start_server():
    print("🚀 Starting AI Meeting Assistant Backend Server...")
    print("=" * 60)
    
    try:
        # Start uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure all dependencies are installed:")
        print("     pip install -r requirements.txt")
        print("  2. Check if port 8000 is already in use")
        print("  3. Verify your .env file has required API keys")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
