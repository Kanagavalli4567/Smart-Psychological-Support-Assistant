import sqlite3
import os

def update_database():
    """Update database schema with all required columns"""
    
    db_path = 'mindmate.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found! Creating new database...")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if users table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = c.fetchone()
    
    if table_exists:
        # Get existing columns in users table
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        print(f"Existing columns in users table: {columns}")
        
        # Add missing columns
        if 'email' not in columns:
            print("Adding 'email' column...")
            c.execute("ALTER TABLE users ADD COLUMN email TEXT")
            print("✅ Added email column")
        
        if 'password_hash' not in columns:
            print("Adding 'password_hash' column...")
            c.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            print("✅ Added password_hash column")
        
        if 'full_name' not in columns:
            print("Adding 'full_name' column...")
            c.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            print("✅ Added full_name column")
        
        if 'last_login' not in columns:
            print("Adding 'last_login' column...")
            c.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
            print("✅ Added last_login column")
    else:
        # Create fresh users table
        print("Creating fresh users table...")
        c.execute('''CREATE TABLE users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      email TEXT UNIQUE NOT NULL,
                      password_hash TEXT NOT NULL,
                      full_name TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_login TIMESTAMP)''')
        print("✅ Created users table with all columns")
    
    # Create conversations table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  user_message TEXT NOT NULL,
                  bot_message TEXT NOT NULL,
                  language TEXT DEFAULT 'en',
                  emotion TEXT DEFAULT 'neutral',
                  recommendations TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    print("✅ conversations table ready")
    
    # Create feedback table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  convo_id INTEGER,
                  recommendation_type TEXT,
                  rating INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    print("✅ feedback table ready")
    
    # Create user_preferences table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS user_preferences
                 (user_id INTEGER PRIMARY KEY,
                  preferred_language TEXT DEFAULT 'auto',
                  enable_voice BOOLEAN DEFAULT 1,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    print("✅ user_preferences table ready")
    
    # Check conversations table columns
    c.execute("PRAGMA table_info(conversations)")
    conv_columns = [column[1] for column in c.fetchall()]
    
    if 'recommendations' not in conv_columns:
        print("Adding 'recommendations' column to conversations...")
        c.execute("ALTER TABLE conversations ADD COLUMN recommendations TEXT")
        print("✅ Added recommendations column")
    
    if 'emotion' not in conv_columns:
        print("Adding 'emotion' column to conversations...")
        c.execute("ALTER TABLE conversations ADD COLUMN emotion TEXT DEFAULT 'neutral'")
        print("✅ Added emotion column")
    
    if 'language' not in conv_columns:
        print("Adding 'language' column to conversations...")
        c.execute("ALTER TABLE conversations ADD COLUMN language TEXT DEFAULT 'en'")
        print("✅ Added language column")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database update complete!")
    
    # Verify the users table structure
    verify_db()

def verify_db():
    """Verify database structure"""
    conn = sqlite3.connect('mindmate.db')
    c = conn.cursor()
    
    print("\n📊 Verifying database structure:")
    
    # Check users table columns
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    print("Users table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Count existing users
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    print(f"\n👥 Total users in database: {user_count}")
    
    conn.close()

if __name__ == "__main__":
    update_database()