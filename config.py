import os

class Config:
    SECRET_KEY = 'meowmeowmeow123'
    MOVIE_FOLDER = 'movies'
    AVATAR_FOLDER = 'pfp'
    USERS_FILE = 'static/user/acc.json'
    
    HOST = '0.0.0.0'
    PORT = 17701
    DEBUG = False
    
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