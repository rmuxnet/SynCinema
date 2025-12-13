# SynCinema - Real-Time Movie Watching Platform

A Flask-based web application for synchronized movie watching with real-time chat, user presence, and social features. Perfect for watching movies together with friends and family remotely.

Unlike services like Teleparty that require all users to have Netflix subscriptions, **SynCinema lets you watch your own movie files together – no subscriptions needed.** 😉

This project is actively used by the lion to watch movies with friends. For easy remote access without port forwarding, we recommend using [TailScale](https://tailscale.com/) to create a secure private network between your devices. The lion personally port forwarded because he doesn't care about the security implications :), but TailScale is the safer option for most users. The application works reliably in real-world usage scenarios.

**SynCinema + qBittorrent custom search plugins = perfect combo.** 😉

While Python might not be the most optimal choice for this type of application, it works well and gets the job done. It's a free and well-functioning self-hosted alternative to paid services.

Yes, there are probably better alternatives out there, but I don't care – this works for my needs. The codebase is currently being rewritten to be more efficient.

I'm not too worried about security since this is just something self-hosted, but I have recently improved it by moving sensitive configuration out of the code.

---

## 🚀 Announcement: Android Frontend App!

We now have a frontend app for Android!  
**UI isn't the best yet, but we're actively developing it:**  
https://github.com/rmuxnet/SynCinema-App

---

## Future Development

The codebase is undergoing active refactoring. Future plans include:

- Android mobile application
- Desktop PC application

These will provide better native experiences across different platforms.

---

## Features

### Core Functionality

- **Synchronized Playback:** Real-time video synchronization across all connected users
- **Multi-format Support:** Supports MP4, WebM, MKV, AVI, MOV, and other video formats
- **User Authentication:** Simple login system with secure session handling

### Social Features

- **Real-time Chat:** Live messaging with typing indicators
- **Message Reactions:** React to messages with emojis
- **Quick Reactions:** Send floating emoji reactions during video playback
- **User Presence:** See who's online and currently watching
- **Avatar Support:** Custom user avatars with image upload support

### User Experience

- **Theater Mode:** Distraction-free fullscreen viewing experience
- **Responsive Design:** Works seamlessly on desktop, tablet, and mobile devices
- **Dark Theme:** Easy on the eyes for extended viewing sessions
- **Connection Status:** Real-time connection monitoring with automatic reconnection

---

## Technology Stack

- **Backend:** Flask with Flask-SocketIO (logic now modularized in `src/`)
- **Frontend:** Vanilla JavaScript with Socket.IO client
- **Styling:** TailWind CSS with responsive design
- **Configuration:** Environment variables via python-dotenv
- **State Management:** Centralized application state

---

## System Requirements

This application has been tested and runs successfully on:

**Development/Test System:**
- OS: Windows 11 Pro x86_64
- CPU: AMD Ryzen 7 7735HS (16 threads) @ 4.80 GHz
- RAM: 16 GB
- Network: 600 Mbps upload

**Tested Mobile Devices:**
- POCO F3 running LineageOS 22.2
- Redmi Turbo 4 Pro
- Huawei laptop (tested on poor network conditions)

**Multi-Device Testing:**
- Successfully tested with 4 devices simultaneously with no sync issues.

**Minimum Requirements:**
- Any modern OS (Windows, macOS, Linux)
- Python 3.7+
- 2 GB RAM minimum

---

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project:**
   ```bash
   git clone https://github.com/rmuxnet/SynCinema
   cd Movie-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Includes Flask, Flask-SocketIO, python-dotenv, and others.

3. **Configure Environment Variables (Important!):**  
   Create a `.env` file in the root directory. You can use the example file as a template:
   ```bash
   cp env_example.txt .env
   ```
   Open `.env` and set your configuration:
   ```
   SECRET_KEY=change_this_to_something_random
   PORT=17701
   HOST=0.0.0.0
   MOVIE_FOLDER=movies
   ```

4. **Configure Users:**  
   The app will automatically create a `static/user/acc.json` file on first run if it doesn't exist (defaulting to admin:password). You can edit this file to add more users:
   ```json
   {
       "your_name": "your_password",
       "friend_name": "friend_password"
   }
   ```

5. **Add Movie Files:**  
   Place your video files in the `movies` folder (or whichever folder you defined in `.env`).

6. **Start the Server:**
   ```bash
   python app.py
   ```

7. **Access the Application:**  
   Go to [http://localhost:17701](http://localhost:17701) (or your configured port).

---

## File Structure

The project uses a `src/` pattern to keep the root directory clean.

```
Movie-app/
├── app.py                  # Entry point (imports from src)
├── .env                    # Secrets & Config (DO NOT COMMIT)
├── env_example.txt         # Template for .env
├── requirements.txt        # Dependencies
├── README.md               # This file
├── src/                    # Source Code
│   ├── __init__.py
│   ├── config.py           # Loads .env vars
│   ├── routes.py           # Flask routes
│   ├── socket_events.py    # SocketIO logic
│   ├── state.py            # App state
│   ├── utils.py            # Helpers
│   └── logging_config.py   # Logger setup
├── movies/                 # Video files
├── pfp/                    # User avatars
└── static/                 # Frontend assets (CSS, JS, JSON)
```

---

## Configuration Options (`.env`)

| Variable        | Default   | Description                                      |
|-----------------|-----------|--------------------------------------------------|
| SECRET_KEY      | change_me | Used for session security. Change this!          |
| PORT            | 17701     | The port the server runs on.                     |
| HOST            | 0.0.0.0   | 0.0.0.0 allows external access; 127.0.0.1 is local only. |
| DEBUG           | False     | Set to True for development logs.                |
| VPN_DETECTION   | False     | Set to True to block VPN users (requires requests). |
| MOVIE_FOLDER    | movies    | Folder path for video files.                     |

---

## Supported Video Formats

- **Primary:** MP4, WebM, M4V (Best compatibility)
- **Secondary:** MKV, AVI, MOV, WMV, FLV

> **Note:** MKV files may have limited browser support. Converting to MP4 is recommended.

---

## Troubleshooting

- **ModuleNotFoundError:**  
  If you see "No module named src", ensure you are running `python app.py` from the root folder, not inside `src/`.

- **Video won't play:**  
  Check if the browser supports the codec (e.g., HEVC in Chrome might require hardware acceleration or extensions).

- **Sync issues:**  
  Check the server logs for "Heartbeat" or "Disconnect" messages.

- **Audio track selection:**  
  Chrome/Edge may disable track selection for some MP4s. This is a browser limitation; audio will still play.

---

## Acknowledgments

Special thanks to my girlfriend for patiently waiting 3 days while this bullshit app got made. Now we can finally watch movies together! ❤️

---