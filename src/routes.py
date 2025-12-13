from flask import render_template, request, session, redirect, url_for, send_from_directory, Response, send_file, jsonify
import os
import re
import logging
from src.config import Config
from src.utils import (load_users, get_user_avatar_url, get_video_mime_type, get_movies_list)
from src.logging_config import CustomRequestLogger

def setup_routes(app, app_logger):
    USERS = load_users()
    request_logger = CustomRequestLogger(app_logger)
    
    @app.after_request
    def after_request(response):
        if hasattr(request, 'environ') and 'werkzeug.request' not in request.environ:
            request_logger.log_request(request, response)
        return response
    
    @app.route('/')
    def index():
        if 'username' not in session:
            return redirect(url_for('login'))
        app_logger.info(f"User {session['username']} accessed main page")
        movies = get_movies_list()
        app_logger.info(f"Found {len(movies)} movies in library")
        from src.state import app_state
        return render_template('index.html', 
                             username=session['username'], 
                             movies=movies,
                             current_movie=app_state.playback_state['current_movie'],
                             get_video_mime_type=get_video_mime_type)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember')
            if username in USERS and USERS[username] == password:
                session['username'] = username
                if remember:
                    session.permanent = True
                    from datetime import timedelta
                    app.permanent_session_lifetime = timedelta(days=30)
                    app_logger.info(f"User {username} logged in successfully (session will persist for 30 days)")
                else:
                    session.permanent = False
                    app_logger.info(f"User {username} logged in successfully")
                return redirect(url_for('index'))
            else:
                app_logger.warning(f"Failed login attempt for username: {username}")
                return render_template('login.html', error='Invalid credentials')
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        username = session.get('username', 'Unknown')
        session.pop('username', None)
        app_logger.info(f"User {username} logged out")
        return redirect(url_for('login'))
    
    @app.route('/movies/<path:filename>')
    def serve_movie(filename):
        if 'username' not in session:
            app_logger.warning(f"Unauthorized movie access attempt for: {filename}")
            return "Unauthorized", 401
        app_logger.info(f"Movie request from {session['username']}: {filename}")
        file_path = os.path.join(Config.MOVIE_FOLDER, filename)
        if not os.path.exists(file_path):
            app_logger.error(f"Movie file not found: {filename}")
            return "File not found", 404
        real_path = os.path.realpath(file_path)
        movies_path = os.path.realpath(Config.MOVIE_FOLDER)
        if not real_path.startswith(movies_path):
            app_logger.warning(f"Security violation - path traversal attempt: {filename}")
            return "Access denied", 403
        file_size = os.path.getsize(file_path)
        mime_type = get_video_mime_type(filename)
        app_logger.info(f"Serving movie: {filename} (size: {file_size} bytes)")
        range_header = request.headers.get('Range')
        if range_header:
            return serve_partial_content(file_path, range_header, mime_type, file_size)
        response = send_from_directory(Config.MOVIE_FOLDER, filename, 
                                     as_attachment=False, 
                                     mimetype=mime_type)
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Type'] = mime_type
        response.headers['Content-Disposition'] = 'inline'
        return response
    
    @app.route('/avatars/<username>')
    def serve_avatar(username):
        if 'username' not in session:
            return "Unauthorized", 401
        for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            test_path = os.path.join(Config.AVATAR_FOLDER, f"{username}{ext}")
            if os.path.exists(test_path):
                return send_from_directory(Config.AVATAR_FOLDER, f"{username}{ext}")
        return "Avatar not found", 404

    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if username in USERS and USERS[username] == password:
            session['username'] = username
            session.permanent = True
            app_logger.info(f"API Login successful: {username}")
            return jsonify({'status': 'success', 'username': username}) 
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

    @app.route('/api/movies')
    def api_movies():
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        movies = get_movies_list()
        return jsonify({'movies': movies})

def serve_partial_content(file_path, range_header, mime_type, file_size):
    try:
        byte_start = 0
        byte_end = file_size - 1
        if range_header:
            match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            if match:
                byte_start = int(match.group(1))
                if match.group(2):
                    byte_end = int(match.group(2))
        byte_start = max(0, byte_start)
        byte_end = min(file_size - 1, byte_end)
        content_length = byte_end - byte_start + 1
        def generate():
            with open(file_path, 'rb') as f:
                f.seek(byte_start)
                remaining = content_length
                while remaining:
                    chunk_size = min(8192, remaining)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                    remaining -= len(chunk)
        return Response(
            generate(),
            206,
            headers={
                'Content-Type': mime_type,
                'Accept-Ranges': 'bytes',
                'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                'Content-Length': str(content_length),
                'Cache-Control': 'no-cache'
            },
            direct_passthrough=True
        )
    except Exception as e:
        logging.error(f"Error serving partial content: {str(e)}")
        response = send_file(file_path, mimetype=mime_type)
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Length'] = str(file_size)
        return response