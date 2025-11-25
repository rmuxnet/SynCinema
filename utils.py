import json
import os
from config import Config

def load_users():
    """Load users from JSON file"""
    try:
        with open(Config.USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        default_users = {"Armandas": "-", "Sofia": "-"}
        os.makedirs(os.path.dirname(Config.USERS_FILE), exist_ok=True)
        with open(Config.USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=4)
        return default_users



def get_user_avatar_url(username):
    """Get avatar URL for a user, checking if image exists"""
    if not os.path.exists(Config.AVATAR_FOLDER):
        return None
    
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        avatar_path = os.path.join(Config.AVATAR_FOLDER, f"{username}{ext}")
        if os.path.exists(avatar_path):
            return f"/avatars/{username}"
    
    return None

def get_video_mime_type(filename):
    """Get MIME type for video file"""
    file_ext = os.path.splitext(filename)[1].lower()
    return Config.VIDEO_MIME_TYPES.get(file_ext, 'video/mp4')

def get_movies_list():
    """Get list of movies from the movies folder"""
    if not os.path.exists(Config.MOVIE_FOLDER):
        return []
    
    all_files = [f for f in os.listdir(Config.MOVIE_FOLDER) 
                 if f.endswith(Config.VIDEO_EXTENSIONS)]
    
    # Sort movies with better browser support first (MP4/WEBM/MKV), then others
    supported_formats = [f for f in all_files if f.endswith(('.mp4', '.webm', '.m4v', '.mkv'))]
    other_formats = [f for f in all_files if not f.endswith(('.mp4', '.webm', '.m4v', '.mkv'))]
    
    return sorted(supported_formats) + sorted(other_formats)