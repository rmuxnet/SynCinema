from datetime import datetime

class AppState:
    def __init__(self):
        self.playback_state = {
            'is_playing': False,
            'current_time': 0,
            'current_movie': None
        }
        self.chat_messages = []
        self.typing_users = set()
        self.active_users = {}
        self.recent_reactions = []
        self.message_reactions = {}
        
    def add_user(self, username, avatar_display, avatar_url):
        self.active_users[username] = {
            'avatar': avatar_display,
            'avatar_url': avatar_url,
            'joined_at': datetime.now().strftime('%H:%M:%S'),
            'is_watching': False,
            'current_time': 0
        }
    
    def remove_user(self, username):
        self.typing_users.discard(username)
        if username in self.active_users:
            del self.active_users[username]
    
    def update_user_status(self, username, is_watching=None, current_time=None):
        if username in self.active_users:
            if is_watching is not None:
                self.active_users[username]['is_watching'] = is_watching
            if current_time is not None:
                self.active_users[username]['current_time'] = current_time
    
    def add_chat_message(self, message):
        from config import Config
        self.chat_messages.append(message)
        if len(self.chat_messages) > Config.MAX_CHAT_MESSAGES:
            removed_message = self.chat_messages.pop(0)
            if removed_message.get('id') in self.message_reactions:
                del self.message_reactions[removed_message['id']]
    
    def add_reaction(self, reaction):
        from config import Config
        self.recent_reactions.append(reaction)
        if len(self.recent_reactions) > Config.MAX_REACTIONS:
            self.recent_reactions.pop(0)
    
    def get_users_update_data(self):
        return {
            'users': list(self.active_users.keys()),
            'count': len(self.active_users),
            'user_details': self.active_users,
            'typing_users': list(self.typing_users)
        }

app_state = AppState()