from datetime import datetime

class AppState:
    """Centralized application state management"""
    def __init__(self):
        # Store current playback state
        self.playback_state = {
            'is_playing': False,
            'current_time': 0,
            'current_movie': None
        }
        
        # Store chat messages
        self.chat_messages = []
        
        # Store typing users
        self.typing_users = set()
        
        # Store active users with presence info
        self.active_users = {}
        
        # Store recent reactions
        self.recent_reactions = []
        
        # Store message reactions
        self.message_reactions = {}
        
    def add_user(self, username, avatar_display, avatar_url):
        """Add user to active users"""
        self.active_users[username] = {
            'avatar': avatar_display,
            'avatar_url': avatar_url,
            'joined_at': datetime.now().strftime('%H:%M:%S'),
            'is_watching': False,
            'current_time': 0
        }
    
    def remove_user(self, username):
        """Remove user from active users and typing"""
        self.typing_users.discard(username)
        if username in self.active_users:
            del self.active_users[username]
    
    def update_user_status(self, username, is_watching=None, current_time=None):
        """Update user's watching status and time"""
        if username in self.active_users:
            if is_watching is not None:
                self.active_users[username]['is_watching'] = is_watching
            if current_time is not None:
                self.active_users[username]['current_time'] = current_time
    
    def add_chat_message(self, message):
        """Add chat message and maintain limit"""
        from config import Config
        
        self.chat_messages.append(message)
        
        # Keep only last MAX_CHAT_MESSAGES messages
        if len(self.chat_messages) > Config.MAX_CHAT_MESSAGES:
            removed_message = self.chat_messages.pop(0)
            # Clean up reactions for removed message
            if removed_message.get('id') in self.message_reactions:
                del self.message_reactions[removed_message['id']]
    
    def add_reaction(self, reaction):
        """Add reaction and maintain limit"""
        from config import Config
        
        self.recent_reactions.append(reaction)
        
        # Keep only last MAX_REACTIONS reactions
        if len(self.recent_reactions) > Config.MAX_REACTIONS:
            self.recent_reactions.pop(0)
    
    def get_users_update_data(self):
        """Get user update data for broadcasting"""
        return {
            'users': list(self.active_users.keys()),
            'count': len(self.active_users),
            'user_details': self.active_users,
            'typing_users': list(self.typing_users)
        }

# Global state instance
app_state = AppState()