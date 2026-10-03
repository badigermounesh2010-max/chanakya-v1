import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = False
    TESTING = False
    OFFLINE_MODE = True
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/chanakya.db')

    @classmethod
    def as_dict(cls):
        return {
            'debug': cls.DEBUG,
            'offline_mode': cls.OFFLINE_MODE,
            'database_path': cls.DATABASE_PATH,
        }

AI_MODELS = {
    'groq': {'enabled': True, 'free': True, 'priority': 1},
    'google_gemini': {'enabled': True, 'free': True, 'priority': 2},
    'openrouter': {'enabled': True, 'free': True, 'priority': 3},
    'ollama': {'enabled': True, 'free': True, 'offline': True, 'priority': 4},
    'openai': {'enabled': bool(os.getenv('OPENAI_API_KEY')), 'free': False, 'priority': 5},
    'anthropic': {'enabled': bool(os.getenv('ANTHROPIC_API_KEY')), 'free': False, 'priority': 6},
}

AUTOMATION_CONFIG = {
    'mouse_enabled': True,
    'keyboard_enabled': True,
    'screen_capture': True,
    'delay': 0.1,
}
