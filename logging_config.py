import logging
import colorama
from colorama import Fore, Style
import socket
import requests

# Initialize colorama for Windows
colorama.init(autoreset=True)

def get_network_ip():
    """Get local network IP address"""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_external_ip():
    """Get external/public IP address"""
    try:
        response = requests.get('https://api.ipify.org', timeout=3)
        return response.text
    except Exception:
        return "Unable to detect"

def setup_logging():
    """Setup custom logging with colors"""
    # Suppress Flask's default logging more aggressively
    logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
    logging.getLogger('socketio').setLevel(logging.CRITICAL)
    logging.getLogger('engineio').setLevel(logging.CRITICAL)
    
    # Also suppress Flask's startup messages
    import werkzeug
    werkzeug.serving._log = lambda *args, **kwargs: None
    
    # Create custom logger
    logger = logging.getLogger('MovieApp')
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with custom formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Custom formatter with colors
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': Fore.CYAN,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.MAGENTA
        }
        
        def format(self, record):
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
            return super().format(record)
    
    formatter = ColoredFormatter(
        f'{Fore.BLUE}[%(asctime)s]{Style.RESET_ALL} %(levelname)s {Fore.WHITE}%(message)s{Style.RESET_ALL}',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

class CustomRequestLogger:
    """Custom request logger for meaningful request tracking"""
    def __init__(self, logger):
        self.logger = logger
        self.ignored_paths = ['/socket.io/', '/static/', '/avatars/', '/favicon.ico']
        self.movie_requests = {}  # Track movie streaming requests
        
    def log_request(self, request, response):
        # Skip noisy requests
        if any(ignored in request.path for ignored in self.ignored_paths):
            return
            
        # Handle movie streaming requests specially
        if '/movies/' in request.path:
            movie_name = request.path.split('/movies/')[-1]
            if movie_name not in self.movie_requests:
                self.movie_requests[movie_name] = True
                self.logger.info(f"Started streaming: {movie_name}")
            return
            
        # Log other meaningful requests
        if request.method == 'GET':
            if request.path == '/':
                self.logger.info(f"User accessed main page")
            elif request.path == '/login':
                self.logger.info(f"Login page accessed")
        elif request.method == 'POST':
            if request.path == '/login':
                # This will be handled in the login route
                pass

def display_startup_banner(config):
    """Display the startup banner"""
    network_ip = get_network_ip()
    external_ip = get_external_ip()
    
    print(f"\n{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA} SynCinema{Style.RESET_ALL}")
    print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    print(f"{Fore.GREEN} Server starting on port {config.PORT}...{Style.RESET_ALL}")
    print(f"{Fore.YELLOW} Movies folder: {config.MOVIE_FOLDER}{Style.RESET_ALL}")
    print(f"{Fore.BLUE} Local: http://127.0.0.1:{config.PORT}{Style.RESET_ALL}")
    print(f"{Fore.BLUE} Network: http://{network_ip}:{config.PORT}{Style.RESET_ALL}")
    print(f"{Fore.BLUE} External: http://{external_ip}:{config.PORT}{Style.RESET_ALL}")
    print(f"{Fore.RED} Press CTRL+C to stop the server{Style.RESET_ALL}")
    print(f"{Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}")
    print("")