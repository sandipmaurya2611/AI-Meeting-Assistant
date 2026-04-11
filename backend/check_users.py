import sqlite3
import os

db_path = 'ai_meeting.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT email, password_hash FROM users')
    users = cursor.fetchall()
    
    for email, pwd_hash in users:
        print(f"{email} | {pwd_hash[:15]}...")
    
    conn.close()
