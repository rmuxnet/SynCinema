from flask import Flask
from flask_socketio import SocketIO
import os
from config import Config
from logging_config import setup_logging, display_startup_banner
from routes import setup_routes
from socket_events import setup_socket_events
from colorama import Fore, Style

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['MOVIE_FOLDER'] = Config.MOVIE_FOLDER
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)
app_logger = setup_logging()

setup_routes(app, app_logger)
setup_socket_events(socketio, app_logger)

if __name__ == '__main__':
    if not os.path.exists(Config.MOVIE_FOLDER):
        os.makedirs(Config.MOVIE_FOLDER)
        app_logger.info(f"Created movies folder: {Config.MOVIE_FOLDER}")
    
    if not os.path.exists(Config.AVATAR_FOLDER):
        os.makedirs(Config.AVATAR_FOLDER)
        app_logger.info(f"Created avatars folder: {Config.AVATAR_FOLDER}")
    
    display_startup_banner(Config)
    app_logger.info("SynCinema server is ready!")
    print("")
    
    try:
        socketio.run(app, debug=Config.DEBUG, host=Config.HOST, port=Config.PORT, log_output=False)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW} Server stopped by user{Style.RESET_ALL}")
    except Exception as e:
        app_logger.error(f"Server error: {e}")
        print(f"{Fore.RED} Server crashed: {e}{Style.RESET_ALL}")