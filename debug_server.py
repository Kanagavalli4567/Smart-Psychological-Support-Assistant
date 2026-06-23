# debug_server.py
import traceback
import sys

def test_imports():
    """Test all imports"""
    try:
        print("Testing imports...")
        from flask import Flask
        print("✅ Flask imported")
        from flask_cors import CORS
        print("✅ Flask-CORS imported")
        from config import Config
        print("✅ Config imported")
        from services.lang import detect_lang
        print("✅ lang service imported")
        from services.emotion import detect_emotion
        print("✅ emotion service imported")
        from services.safety import is_crisis, crisis_message, is_physical_symptom, physical_symptom_message
        print("✅ safety service imported")
        from services.groq_llm import GroqChatModel
        print("✅ groq_llm imported")
        from services.stt_whisper import transcribe_audio
        print("✅ stt_whisper imported")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_database():
    """Test database connection"""
    try:
        print("\nTesting database...")
        import sqlite3
        from config import Config
        conn = sqlite3.connect(Config.DATABASE_PATH)
        c = conn.cursor()
        
        # Check conversations table schema
        c.execute("PRAGMA table_info(conversations)")
        columns = c.fetchall()
        print(f"Conversations table columns: {[col[1] for col in columns]}")
        
        # Check if recommendations column exists
        has_recommendations = any(col[1] == 'recommendations' for col in columns)
        if not has_recommendations:
            print("⚠️ 'recommendations' column is missing!")
            print("Run: ALTER TABLE conversations ADD COLUMN recommendations TEXT")
        else:
            print("✅ recommendations column exists")
            
        conn.close()
        return has_recommendations
    except Exception as e:
        print(f"❌ Database error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Debugging MindMate Server ===\n")
    
    imports_ok = test_imports()
    if not imports_ok:
        print("\n❌ Fix import errors first")
        sys.exit(1)
    
    db_ok = test_database()
    if not db_ok:
        print("\n⚠️ Database needs migration")
        
    print("\n✅ Debug complete")