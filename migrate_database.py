# migrate_database.py
import sqlite3
import os
from config import Config

def migrate_database():
    """Add missing columns to database"""
    
    db_path = Config.DATABASE_PATH
    print(f"Migrating database: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Creating new database...")
        # Database will be created by init_db in app.py
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get existing columns
    c.execute("PRAGMA table_info(conversations)")
    existing_columns = [col[1] for col in c.fetchall()]
    print(f"Existing columns: {existing_columns}")
    
    # Add missing columns
    columns_to_add = {
        'recommendations': 'TEXT',
        'emotion': 'TEXT DEFAULT "neutral"',
        'language': 'TEXT DEFAULT "en"'
    }
    
    for col_name, col_type in columns_to_add.items():
        if col_name not in existing_columns:
            try:
                print(f"Adding column: {col_name}")
                c.execute(f"ALTER TABLE conversations ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added {col_name} column")
            except Exception as e:
                print(f"⚠️ Could not add {col_name}: {e}")
    
    conn.commit()
    
    # Verify columns now exist
    c.execute("PRAGMA table_info(conversations)")
    updated_columns = [col[1] for col in c.fetchall()]
    print(f"\nUpdated columns: {updated_columns}")
    
    conn.close()
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    migrate_database()