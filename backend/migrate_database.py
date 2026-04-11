"""
Migration script to add password_hash and is_active fields to the users table.
This script safely updates the existing database schema.
"""

import sqlite3
import os

db_path = 'ai_meeting.db'

def migrate_database():
    if not os.path.exists(db_path):
        print("❌ Database doesn't exist. No migration needed.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Starting database migration...")
    
    try:
        # Check if columns already exist
        cursor.execute('PRAGMA table_info(users)')
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"📊 Current columns: {', '.join(columns)}")
        
        # Add password_hash column if it doesn't exist
        if 'password_hash' not in columns:
            print("➕ Adding password_hash column...")
            cursor.execute('''
                ALTER TABLE users 
                ADD COLUMN password_hash VARCHAR DEFAULT 'temporary_hash_please_reset'
            ''')
            print("✅ Added password_hash column")
        else:
            print("⏭️  password_hash column already exists")
        
        # Add is_active column if it doesn't exist
        if 'is_active' not in columns:
            print("➕ Adding is_active column...")
            cursor.execute('''
                ALTER TABLE users 
                ADD COLUMN is_active BOOLEAN DEFAULT 1
            ''')
            print("✅ Added is_active column")
        else:
            print("⏭️  is_active column already exists")
        
        conn.commit()
        
        # Verify the changes
        cursor.execute('PRAGMA table_info(users)')
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"\n📊 Updated columns: {', '.join(new_columns)}")
        
        print("\n✅ Migration completed successfully!")
        print("\n⚠️  IMPORTANT: Existing users have a temporary password hash.")
        print("   They will need to re-register or you can manually update their passwords.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
