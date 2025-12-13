from flask_socketio import emit, join_room, leave_room, disconnect
from datetime import datetime
import requests
from src.utils import get_user_avatar_url
from src.config import Config
from src.state import app_state

def is_vpn(ip_address):
    try:
        if ip_address in ['127.0.0.1', '::1', 'localhost']:
            return False

        response = requests.get(
            f"http://ip-api.com/json/{ip_address}?fields=status,proxy,hosting",
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return data.get('proxy', False) or data.get('hosting', False)
    except Exception:
        pass
    return False

def setup_socket_events(socketio, app_logger):
    
    @socketio.on('connect')
    def handle_connect():
        from flask import session, request
        
        client_ip = request.remote_addr
        if Config.VPN_DETECTION_ENABLED and is_vpn(client_ip):
            app_logger.warning(f"Connection rejected for user {session.get('username', 'Unknown')} from IP {client_ip} (VPN Detected)")
            disconnect()
            return

        if 'username' in session:
            avatar_url = get_user_avatar_url(session['username'])
            avatar_display = avatar_url if avatar_url else Config.USER_AVATARS.get(session['username'], Config.USER_AVATARS['default'])
            app_state.add_user(session['username'], avatar_display, avatar_url)
            join_room('movie_room')
            app_logger.info(f"User {session['username']} connected to movie room from IP: {client_ip}")
            emit('user_joined', {
                'username': session['username'],
                'avatar': avatar_display,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }, room='movie_room')
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
            emit('sync_state', app_state.playback_state)
            chat_history = []
            for msg in app_state.chat_messages:
                if 'spoiler' not in msg:
                    msg['spoiler'] = False
                chat_history.append(msg)
            emit('chat_history', chat_history)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        from flask import session, request
        if 'username' in session:
            app_state.typing_users.discard(session['username'])
            emit('user_stopped_typing', {
                'username': session['username']
            }, room='movie_room')
            app_state.remove_user(session['username'])
            app_logger.info(f"User {session['username']} disconnected from movie room (IP: {request.remote_addr})")
            emit('user_left', {
                'username': session['username'],
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }, room='movie_room')
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
            leave_room('movie_room')
    
    @socketio.on('play')
    def handle_play(data):
        from flask import session
        if 'username' in session:
            app_state.playback_state['is_playing'] = True
            app_state.playback_state['current_time'] = data.get('time', 0)
            app_state.update_user_status(session['username'], 
                                       is_watching=True, 
                                       current_time=data.get('time', 0))
            emit('play_video', {
                'time': app_state.playback_state['current_time'],
                'username': session['username']
            }, room='movie_room', include_self=False)
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
    
    @socketio.on('pause')
    def handle_pause(data):
        from flask import session
        if 'username' in session:
            app_state.playback_state['is_playing'] = False
            app_state.playback_state['current_time'] = data.get('time', 0)
            app_state.update_user_status(session['username'], 
                                       is_watching=False, 
                                       current_time=data.get('time', 0))
            emit('pause_video', {
                'time': app_state.playback_state['current_time'],
                'username': session['username']
            }, room='movie_room', include_self=False)
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
                'spoiler': data.get('spoiler', False)
            }
            app_state.add_chat_message(message)
            app_state.message_reactions[message_id] = {}
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
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
    
    @socketio.on('stop_typing')
    def handle_stop_typing():
        from flask import session
        if 'username' in session:
            app_state.typing_users.discard(session['username'])
            emit('user_stopped_typing', {
                'username': session['username']
            }, room='movie_room')
            emit('users_update', app_state.get_users_update_data(), room='movie_room')
    
    @socketio.on('heartbeat')
    def handle_heartbeat(data):
        from flask import session
        if 'username' in session:
            app_state.update_user_status(session['username'],
                                       is_watching=data.get('is_watching', False),
                                       current_time=data.get('time', 0))
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
                message = None
                for msg in app_state.chat_messages:
                    if msg.get('id') == message_id:
                        message = msg
                        break
                if message:
                    if 'reactions' not in message:
                        message['reactions'] = {}
                    if message_id not in app_state.message_reactions:
                        app_state.message_reactions[message_id] = {}
                    if emoji in message['reactions']:
                        if session['username'] in message['reactions'][emoji]:
                            message['reactions'][emoji].remove(session['username'])
                            if len(message['reactions'][emoji]) == 0:
                                del message['reactions'][emoji]
                        else:
                            message['reactions'][emoji].append(session['username'])
                    else:
                        message['reactions'][emoji] = [session['username']]
                    emit('message_reaction_update', {
                        'message_id': message_id,
                        'reactions': message['reactions'],
                        'user': session['username']
                    }, room='movie_room', include_self=True)