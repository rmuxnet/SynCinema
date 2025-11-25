# SynCinema - Real-Time Movie Watching Platform

A Flask-based web application that enables synchronized movie watching sessions with real-time chat, user presence tracking, and social features. Perfect for watching movies together with friends and family remotely.

Unlike services like Teleparty that require all users to have Netflix subscriptions, SynCinema lets you watch your own movie files together - no subscriptions needed 😉

This project is actively used by the lion to watch movies with friends. For easy remote access without port forwarding, we recommend using TailScale to create a secure private network between your devices. The lion personally port forwarded because he doesn't care about the security implications :) but TailScale is the safer option for most users. The application works reliably in real-world usage scenarios.

SynCinema + qBittorrent custom search plugins = perfect combo 😉

While Python might not be the most optimal choice for this type of application, it works well and gets the job done. It's not much, but it's a free and well-functioning self-hosting alternative to paid services.

Yes, there are probably better alternatives out there, but I don't care - this works for my needs. The codebase will be rewritten soon to be more efficient in general.

I'm not too worried about security since this is just something self-hosted, but yes, I will improve it.

## Future Development

The codebase will be rewritten soon with plans to develop:
- Android mobile application
- Desktop PC application

These will provide better native experiences across different platforms.

## Features

### Core Functionality
- **Synchronized Playback**: Real-time video synchronization across all connected users
- **Multi-format Support**: Supports MP4, WebM, MKV, AVI, MOV, and other video formats
- **User Authentication**: Secure login system with customizable user accounts

### Social Features
- **Real-time Chat**: Live messaging with typing indicators
- **Message Reactions**: React to messages with emojis
- **Quick Reactions**: Send floating emoji reactions during video playback
- **User Presence**: See who's online and currently watching
- **Avatar Support**: Custom user avatars with image upload support

### User Experience
- **Theater Mode**: Distraction-free fullscreen viewing experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Dark Theme**: Easy on the eyes for extended viewing sessions
- **Connection Status**: Real-time connection monitoring with automatic reconnection

## Technology Stack

- **Backend**: Flask with Flask-SocketIO for real-time communication
- **Frontend**: Vanilla JavaScript with Socket.IO client
- **Styling**: TailWind CSS with responsive design
- **File Handling**: Direct video streaming with MIME type detection
- **State Management**: Centralized application state with user session tracking

## System Requirements

This application has been tested and runs successfully on:

**Development/Test System:**
- OS: Windows 11 Pro x86_64 (Build 10.0.26100.4946)
- CPU: AMD Ryzen 7 7735HS (16 threads) @ 4.80 GHz
- RAM: 16 GB.
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU + AMD Radeon Graphics
- Internet: 600 Mbps upload (5ms unloaded, 89ms loaded latency)
- Python: 3.x with Flask and dependencies

**Tested Mobile Devices:**
- POCO F3 running LineageOS 22.2 - Ran fine without issues
- Redmi Turbo 4 Pro

**Additional Tested Devices:**
- Huawei laptop - Works fine even on poor network conditions (tested from another country)

**Multi-Device Testing:**
- Successfully tested with 4 devices simultaneously (host PC, Huawei laptop, POCO F3, Redmi Turbo 4 Pro) - No issues whatsoever

**Minimum Requirements:**
- Any modern operating system (Windows, macOS, Linux)
- Python 3.7 or higher
- 2 GB RAM minimum
- Network connectivity for multi-user sessions

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project** to your desired directory
2. **Navigate to the project directory**:
   ```bash
   cd Movie-app
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Required packages:
   - Flask==2.3.3
   - Flask-SocketIO==5.3.6
   - colorama==0.4.6
   - python-socketio==5.8.0
   - python-engineio==4.7.1
   - Werkzeug==2.3.7

4. **Configure user accounts** by editing `static/user/acc.json`:
   ```json
   {
       "username1": "password1",
       "username2": "password2"
   }
   ```

5. **Add your movie files** to the `movies` folder

6. **Start the server**:
   ```bash
   python app.py
   ```

7. **Access the application** at `http://localhost:17701`

## Configuration

### Server Settings
Edit `config.py` to customize server behavior:

- `HOST`: Server host address (default: '0.0.0.0')
- `PORT`: Server port (default: 17701)
- `DEBUG`: Enable debug mode (default: False)

### File Locations
- `MOVIE_FOLDER`: Directory containing video files (default: 'movies')
- `AVATAR_FOLDER`: Directory for user avatar images (default: 'pfp')
- `USERS_FILE`: User accounts configuration (default: 'static/user/acc.json')

### Chat Settings
- `MAX_CHAT_MESSAGES`: Maximum chat history (default: 100)
- `MAX_REACTIONS`: Maximum stored reactions (default: 50)
- `MIN_SAVE_TIME`: Minimum watch time before saving progress (default: 10 seconds)

## Usage

### For Users
1. **Login** with your assigned username and password
2. **Select a movie** from the dropdown menu
3. **Control playback** - play, pause, and seek actions are synchronized across all users
4. **Chat** with other viewers using the chat panel
5. **React** to movies using quick reaction buttons or message reactions
6. **Toggle theater mode** for an immersive viewing experience

### For Administrators
1. **Add movies** by placing video files in the `movies` directory
2. **Manage users** by editing the `acc.json` file
3. **Add avatars** by placing image files in the `pfp` directory with filenames matching usernames
4. **Monitor logs** for connection and error information

## Supported Video Formats

- **Primary**: MP4, WebM, M4V (best browser compatibility)
- **Secondary**: MKV, AVI, MOV, WMV, FLV, 3GP, OGV, TS, MTS, VOB

Note: MKV files may have limited browser support. Consider converting to MP4 for best compatibility.

## File Structure

```
Movie-app/
├── app.py                 # Main application entry point
├── config.py             # Configuration settings
├── routes.py             # Flask route handlers
├── socket_events.py      # Socket.IO event handlers
├── state.py              # Application state management
├── utils.py              # Utility functions
├── logging_config.py     # Logging configuration
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── movies/              # Video files directory (created automatically)
├── pfp/                 # User avatar images (created automatically)
├── static/
│   ├── css/
│   │   ├── tailwind.css         # Main application styles
│   │   └── login-tailwind.css   # Login page styles
│   ├── js/
│   │   ├── index.js            # Main frontend JavaScript
│   │   ├── stars-animation.js  # Login page animation
│   │   └── login.js            # Login page functionality
│   ├── img/
│   │   └── logo.png            # Application logo
│   └── user/
│       └── acc.json            # User accounts
└── templates/
    ├── index.html       # Main application template
    └── login.html       # Login page template
```

## API Documentation

### Socket.IO Events

#### Client to Server
- `play`: Broadcast play command with timestamp
- `pause`: Broadcast pause command with timestamp
- `seek`: Broadcast seek command with new timestamp
- `change_movie`: Change current movie for all users
- `send_message`: Send chat message
- `send_reaction`: Send floating emoji reaction
- `react_to_message`: React to a specific chat message
- `typing`/`stop_typing`: Typing indicator events
- `heartbeat`: User presence updates

#### Server to Client
- `play_video`/`pause_video`/`seek_video`: Playback synchronization
- `movie_changed`: Movie selection updates
- `new_message`: New chat messages
- `user_joined`/`user_left`: User presence updates
- `users_update`: Online user list updates
- `new_reaction`: Floating emoji reactions
- `message_reaction_update`: Message reaction updates

## Security Features

- Session-based authentication
- Path traversal protection for file serving
- CORS configuration for Socket.IO
- Input validation and sanitization
- Secure file serving with MIME type validation

## Browser Compatibility

- **Recommended**: Chrome, Edge, Safari (latest versions)
- **Mobile**: iOS Safari, Chrome Mobile.
- **Video Support**: Depends on browser codec support

## Performance Considerations

- Video files are streamed directly without transcoding
- Chat history is limited to prevent memory issues
- Automatic cleanup of old reactions and messages
- Efficient state management with minimal data transfer

## Troubleshooting

### Common Issues

1. **Video won't play**: Check file format compatibility with your browser. MKV files often have limited browser support - consider converting to MP4.
2. **Sync issues**: Ensure stable internet connection for all users. Check heartbeat interval (5 seconds) is functioning properly.
3. **Login problems**: Verify credentials in `static/user/acc.json`
4. **File not found**: Ensure video files are in the `movies` directory with correct permissions
5. **Audio track controls grayed out**: This is a browser limitation for certain MP4 files. Audio still works normally, but track selection may not be available in Chrome/Edge.
6. **Connection lost**: Application automatically attempts reconnection. Check server logs for disconnect reasons.

### Known Limitations

- **MKV Browser Support**: MKV files may not work in most browsers due to codec limitations. MP4, WebM, and M4V are recommended for best compatibility.
- **Audio Track Selection**: Chrome and Edge may disable audio track selection controls for some MP4 files, even when multiple audio tracks exist. This is a browser limitation, not a server issue. The audio will still play normally.
- **Large File Support**: Files over 2GB are supported via HTTP range requests, but initial loading may take longer depending on network speed.
- **Mobile Scrolling**: On some mobile devices, chat scrolling behavior may vary. The app auto-scrolls when new messages arrive unless manually scrolled up.

### Logs
Check the console output for detailed error messages and connection information. The application uses colored logging for easy reading:

- **GREEN**: Info messages (successful operations)
- **YELLOW**: Warnings (non-critical issues)
- **RED**: Errors (critical issues)
- **CYAN**: Debug information

**Example log output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SynCinema
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Server starting on port 17701...
 Movies folder: movies
 Local: http://127.0.0.1:17701
 Network: http://localnet:17701
 External: http://yesmeip:17701
 Press CTRL+C to stop the server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[14:43:37] INFO Movie request from Dev: Alice.in.Borderland.S01E04.DUBBED.1080p.WEBRip.x265-RARBG[eztv.re].mp4
[14:43:37] INFO Serving movie: Alice.in.Borderland.S01E04.DUBBED.1080p.WEBRip.x265-RARBG[eztv.re].mp4 (size: 791516568 bytes)
[14:43:38] INFO User Dev connected to movie room
[14:44:40] INFO Movie request from Dev_Gf: Finding.Nemo.2003.720p.BluRay.x264.YIFY.mp4
[14:45:01] INFO User Dev disconnected from movie room
[15:01:05] INFO User Dev_Gf accessed main page
[15:01:05] INFO Found 17 movies in library
```

## Contributing

1. Follow the existing code structure and naming conventions
2. Test changes with multiple users for synchronization issues
3. Ensure mobile compatibility for new features
4. Update documentation for any configuration changes

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions, please provide detailed logs from the console output along with your bug report. Include information about:
- Browser type and version
- Number of connected users when the issue occurred
- Console error messages (if any)
- Steps to reproduce the problem

Check the application logs first as they often contain helpful error messages and connection information.

## Acknowledgments

Special thanks to my girlfriend for patiently waiting 3 days while this bullshit app got made. Now we can finally watch movies together! ❤️