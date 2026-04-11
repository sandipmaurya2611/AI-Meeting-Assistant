import sqlite3
import bcrypt

db_path = 'ai_meeting.db'
target_email = "mauryasandip4you@gmail.com"
new_password = "password123"

# Generate new hash using the SAME logic as the app
pwd_bytes = new_password.encode('utf-8')
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(pwd_bytes, salt)
hashed_str = hashed.decode('utf-8')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if user exists
cursor.execute("SELECT id FROM users WHERE email = ?", (target_email,))
user = cursor.fetchone()

if user:
    print(f"Found user: {target_email}")
    cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (hashed_str, target_email))
    conn.commit()
    print(f"✅ Password updated to: {new_password}")
else:
    print(f"❌ User {target_email} not found!")

conn.close()
