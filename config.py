import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'mindmate.db')
    WHISPER_MODEL = os.environ.get('WHISPER_MODEL', 'base')
    ENABLE_CRISIS_CHECK = os.environ.get('ENABLE_CRISIS_CHECK', 'True').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GROQ_API_KEY:
            print("⚠️ Warning: GROQ_API_KEY not set. Running in fallback mode.")
        return True

# Validate on import
Config.validate()