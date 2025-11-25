from flask_socketio import emit, join_room, leave_room
from datetime import datetime
from utils import get_user_avatar_url
from config import Config
from state import app_state

def setup_socket_events(socketio, app_logger):
    """Setup all Socket.IO events"""
    
    @socketio.on('connect')
    def handle_connect():
        from flask import session
        if 'username' in session:
            # Get avatar URL or use emoji fallback
            avatar_url = get_user_avatar_url(session['username'])
            avatar_display = avatar_url if avatar_url else Config.USER_AVATARS.get(session['username'], Config.USER_AVATARS['default'])
            
            # Add user to active users
            app_state.add_user(session['username'], avatar_display, avatar_url)
            
            join_room('movie_room')
            app_logger.info(f"User {session['username']} connected to movie room")
            
            emit('user_joined', {
                'username': session['username'],
                'avatar': avatar_display,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }, room='movie_room')
            
            # Send updated user list to everyone
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
            
            # Send current playback state to newly connected user
            emit('sync_state', app_state.playback_state)
            
            # Send chat history
            # Ensure all messages have 'spoiler' property
            chat_history = []
            for msg in app_state.chat_messages:
                if 'spoiler' not in msg:
                    msg['spoiler'] = False
                chat_history.append(msg)
            emit('chat_history', chat_history)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        from flask import session
        if 'username' in session:
            # Remove user from typing users if they were typing
            app_state.typing_users.discard(session['username'])
            emit('user_stopped_typing', {
                'username': session['username']
            }, room='movie_room')
            
            # Remove user from active users
            app_state.remove_user(session['username'])
            
            app_logger.info(f"User {session['username']} disconnected from movie room")
            
            emit('user_left', {
                'username': session['username'],
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }, room='movie_room')
            
            # Send updated user list to everyone
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
            
            leave_room('movie_room')
    
    @socketio.on('play')
    def handle_play(data):
        from flask import session
        if 'username' in session:
            app_state.playback_state['is_playing'] = True
            app_state.playback_state['current_time'] = data.get('time', 0)
            
            # Update user watching status
            app_state.update_user_status(session['username'], 
                                       is_watching=True, 
                                       current_time=data.get('time', 0))
            
            emit('play_video', {
                'time': app_state.playback_state['current_time'],
                'username': session['username']
            }, room='movie_room', include_self=False)
            
            # Send updated user list
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
    
    @socketio.on('pause')
    def handle_pause(data):
        from flask import session
        if 'username' in session:
            app_state.playback_state['is_playing'] = False
            app_state.playback_state['current_time'] = data.get('time', 0)
            
            # Update user watching status
            app_state.update_user_status(session['username'], 
                                       is_watching=False, 
                                       current_time=data.get('time', 0))
            
            emit('pause_video', {
                'time': app_state.playback_state['current_time'],
                'username': session['username']
            }, room='movie_room', include_self=False)
            
            # Send updated user list
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
    
    @socketio.on('seek')
    def handle_seek(data):
        from flask import session
        if 'username' in session:
            app_state.playback_state['current_time'] = data.get('time', 0)
            emit('seek_video', {
                'time': app_state.playback_state['current_time'],
                'username': session['username']
            }, room='movie_room', include_self=False)
    
    @socketio.on('change_movie')
    def handle_change_movie(data):
        from flask import session
        
        if 'username' in session:
            new_movie = data.get('movie')
            app_state.playback_state['current_movie'] = new_movie
            app_state.playback_state['current_time'] = 0
            app_state.playback_state['is_playing'] = False
            
            emit('movie_changed', {
                'movie': app_state.playback_state['current_movie'],
                'time': app_state.playback_state['current_time'],
                'username': session['username']
            }, room='movie_room', include_self=True)
    
    @socketio.on('send_message')
    def handle_message(data):
        from flask import session
        if 'username' in session:
            message_id = f"{len(app_state.chat_messages)}_{session['username']}_{datetime.now().timestamp()}"
            avatar_url = get_user_avatar_url(session['username'])
            message = {
                'id': message_id,
                'username': session['username'],
                'avatar': avatar_url if avatar_url else Config.USER_AVATARS.get(session['username'], Config.USER_AVATARS['default']),
                'avatar_url': avatar_url,
                'message': data.get('message'),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'reactions': {},
                'spoiler': data.get('spoiler', False)  # <-- Add spoiler property
            }
            
            app_state.add_chat_message(message)
            
            # Initialize reactions for this message
            app_state.message_reactions[message_id] = {}
            
            # Remove user from typing when they send a message
            app_state.typing_users.discard(session['username'])
            emit('user_stopped_typing', {
                'username': session['username']
            }, room='movie_room')
            
            emit('new_message', message, room='movie_room', include_self=True)
    
    @socketio.on('typing')
    def handle_typing():
        from flask import session
        if 'username' in session:
            app_state.typing_users.add(session['username'])
            avatar_url = get_user_avatar_url(session['username'])
            avatar_display = avatar_url if avatar_url else Config.USER_AVATARS.get(session['username'], Config.USER_AVATARS['default'])
            
            emit('user_typing', {
                'username': session['username'],
                'avatar': avatar_display
            }, room='movie_room', include_self=False)
            
            # Send updated user list to show typing status
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
    
    @socketio.on('stop_typing')
    def handle_stop_typing():
        from flask import session
        if 'username' in session:
            app_state.typing_users.discard(session['username'])
            emit('user_stopped_typing', {
                'username': session['username']
            }, room='movie_room')
            
            # Send updated user list to remove typing status
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
    
    @socketio.on('heartbeat')
    def handle_heartbeat(data):
        from flask import session
        if 'username' in session:
            # Update user's current video time and watching status
            app_state.update_user_status(session['username'],
                                       is_watching=data.get('is_watching', False),
                                       current_time=data.get('time', 0))
            
            # Send updated user list periodically
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
    
    @socketio.on('send_reaction')
    def handle_reaction(data):
        from flask import session
        if 'username' in session:
            avatar_url = get_user_avatar_url(session['username'])
            avatar_display = avatar_url if avatar_url else Config.USER_AVATARS.get(session['username'], Config.USER_AVATARS['default'])
            
            reaction = {
                'username': session['username'],
                'avatar': avatar_display,
                'emoji': data.get('emoji'),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'video_time': data.get('video_time', 0)
            }
            
            app_state.add_reaction(reaction)
            
            emit('new_reaction', reaction, room='movie_room', include_self=True)
    
    @socketio.on('react_to_message')
    def handle_message_reaction(data):
        from flask import session
        if 'username' in session:
            message_id = data.get('message_id')
            emoji = data.get('emoji')
            
            if message_id and emoji:
                # Find the message
                message = None
                for msg in app_state.chat_messages:
                    if msg.get('id') == message_id:
                        message = msg
                        break
                
                if message:
                    # Initialize reactions if not exists
                    if 'reactions' not in message:
                        message['reactions'] = {}
                    if message_id not in app_state.message_reactions:
                        app_state.message_reactions[message_id] = {}
                    
                    # Toggle reaction for this user
                    if emoji in message['reactions']:
                        if session['username'] in message['reactions'][emoji]:
                            # Remove reaction
                            message['reactions'][emoji].remove(session['username'])
                            if len(message['reactions'][emoji]) == 0:
                                del message['reactions'][emoji]
                        else:
                            # Add reaction
                            message['reactions'][emoji].append(session['username'])
                    else:
                        # Create new reaction
                        message['reactions'][emoji] = [session['username']]
                    
                    # Emit updated message reactions to all users
                    emit('message_reaction_update', {
                        'message_id': message_id,
                        'reactions': message['reactions'],
                        'user': session['username']
                    }, room='movie_room', include_self=True)