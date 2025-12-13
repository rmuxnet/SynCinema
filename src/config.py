import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 17701))
    
    @staticmethod
    def get_bool_env(var_name, default=False):
        val = os.getenv(var_name, str(default)).lower()
        return val in ['true', '1', 't', 'y', 'yes']

    DEBUG = get_bool_env('DEBUG', False)
    VPN_DETECTION_ENABLED = get_bool_env('VPN_DETECTION_ENABLED', False)
    MOVIE_FOLDER = os.path.join(BASE_DIR, os.getenv('MOVIE_FOLDER', 'movies'))
    AVATAR_FOLDER = os.path.join(BASE_DIR, os.getenv('AVATAR_FOLDER', 'pfp'))
    USERS_FILE = os.path.join(BASE_DIR, os.getenv('USERS_FILE', 'static/user/acc.json'))
    MAX_CHAT_MESSAGES = 100
    MAX_REACTIONS = 50
    MIN_SAVE_TIME = 10
    VIDEO_MIME_TYPES = {
        '.mp4': 'video/mp4',
        '.mkv': 'video/x-matroska',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.wmv': 'video/x-ms-wmv',
        '.flv': 'video/x-flv',
        '.webm': 'video/webm',
        '.m4v': 'video/mp4',
        '.3gp': 'video/3gpp',
        '.ogv': 'video/ogg',
        '.ts': 'video/mp2t',
        '.mts': 'video/mp2t',
        '.vob': 'video/dvd'
    }
    VIDEO_EXTENSIONS = tuple(VIDEO_MIME_TYPES.keys())