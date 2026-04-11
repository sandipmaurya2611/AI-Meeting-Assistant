import sqlite3
import os

db_path = 'ai_meeting.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Current User table schema:")
    cursor.execute('PRAGMA table_info(users)')
    for row in cursor.fetchall():
        print(f"  {row[1]} ({row[2]})")
    
    conn.close()
    print("\nNote: The database needs to be recreated to include password_hash field.")
    print("You can either:")
    print("  1. Delete ai_meeting.db and restart the server (it will recreate)")
    print("  2. Or use Alembic migrations to update the schema")
else:
    print("Database doesn't exist yet. It will be created on first server start.")
