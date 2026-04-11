import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

async def verify():
    url = os.getenv("DATABASE_URL")
    print(f"Testing primary connection: {url}")
    
    try:
        # Try original URL first
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT version()"))
            print(f"SUCCESS (Primary): {res.scalar()}")
            return
    except Exception as e:
        print(f"Primary connection failed: {e}")
    
    # Fallback for local execution if using docker internal hostname "postgres"
    if "postgres:5432" in url:
        print("Attempting fallback to localhost:5433 for local execution...")
        # Replace host and port for local access
        fallback_url = url.replace("postgres:5432", "localhost:5433")
        try:
            engine = create_async_engine(fallback_url)
            async with engine.connect() as conn:
                res = await conn.execute(text("SELECT version()"))
                print(f"SUCCESS (Fallback): {res.scalar()}")
        except Exception as e:
             print(f"Fallback connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
