const socket = io();
const video = document.getElementById('videoPlayer');
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const movieSelector = document.getElementById('movieSelector');
const status = document.getElementById('status');

let isSyncing = false;
let lastSeekTime = 0;
let seekTimeout = null;
let isTheaterMode = false;
let typingTimeout = null;
let isTyping = false;
let heartbeatInterval = null;
let userScrolledUp = false;
let autoScrollEnabled = true;

socket.on('connect', () => {
    status.textContent = 'Connected';
    status.style.background = '#2d5016';
    
    const connStatus = document.getElementById('connectionStatus');
    if (connStatus) {
        connStatus.textContent = 'Connected';
        connStatus.classList.remove('disconnected');
    }
    
    heartbeatInterval = setInterval(() => {
        if (video) {
            socket.emit('heartbeat', {
                time: video.currentTime,
                is_watching: !video.paused
            });
        }
    }, 5000);
});

socket.on('disconnect', () => {
    status.textContent = 'Disconnected - Reconnecting...';
    status.style.background = '#5a1a1a';
    
    const connStatus = document.getElementById('connectionStatus');
    if (connStatus) {
        connStatus.textContent = 'Reconnecting...';
        connStatus.classList.add('disconnected');
    }
    
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
});

socket.on('sync_state', (state) => {
    if (video && state.current_time) {
        video.currentTime = state.current_time;
    }
});

socket.on('play_video', (data) => {
    if (video && !isSyncing) {
        isSyncing = true;
        video.currentTime = data.time;
        video.play();
        addSystemMessage(`${data.username} played the video`);
        setTimeout(() => isSyncing = false, 100);
    }
});

socket.on('pause_video', (data) => {
    if (video && !isSyncing) {
        isSyncing = true;
        video.currentTime = data.time;
        video.pause();
        addSystemMessage(`${data.username} paused the video`);
        setTimeout(() => isSyncing = false, 100);
    }
});

socket.on('seek_video', (data) => {
    if (video && !isSyncing) {
        isSyncing = true;
        lastSeekTime = data.time;
        video.currentTime = data.time;
        addSystemMessage(`${data.username} seeked to ${formatTime(data.time)}`);
        setTimeout(() => isSyncing = false, 500);
    }
});

socket.on('movie_changed', (data) => {
    if (!isSyncing) {
        addSystemMessage(`${data.username} changed the movie to: ${data.movie}`);
        
        movieSelector.value = data.movie;

        if (video && data.movie) {
            const newSrc = `/movies/${encodeURIComponent(data.movie)}`;
            
            enhanceVideoElement();
            
            video.src = newSrc;
            video.load();
            
            if (data.time && data.time > 0) {
                video.currentTime = data.time;
                if (data.time > 30) {
                    addSystemMessage(`Resumed from ${formatTime(data.time)}`);
                }
            } else {
                video.currentTime = 0;
            }
            
            addSystemMessage('Switching video...');
        } else if (!data.movie) {
            if (video) {
                video.src = '';
                video.load();
            }
            addSystemMessage('No movie selected');
        }
    }
});

socket.on('users_update', (data) => {
    updateUserList(data.users, data.count, data.user_details, data.typing_users || []);
});

socket.on('user_joined', (data) => {
    // Only show username for join messages, avatar is handled in user list
    addSystemMessage(`${data.username} joined the room`);
});

socket.on('user_left', (data) => {
    addSystemMessage(`${data.username} left the room`);
});

socket.on('new_message', (data) => {
    const isSpoiler = typeof data.spoiler === 'boolean' ? data.spoiler : false;
    addMessage(data.username, data.message, data.timestamp, data.avatar, data.id, data.reactions, true, isSpoiler);
});

socket.on('chat_history', (messages) => {
    messages.forEach(msg => {
        const isSpoiler = typeof msg.spoiler === 'boolean' ? msg.spoiler : false;
        addMessage(msg.username, msg.message, msg.timestamp, msg.avatar, msg.id, msg.reactions, false, isSpoiler);
    });
});

socket.on('message_reaction_update', (data) => {
    updateMessageReactions(data.message_id, data.reactions);
});

socket.on('user_typing', (data) => {
    showTypingIndicator(data.username, data.avatar);
});

socket.on('user_stopped_typing', (data) => {
    hideTypingIndicator(data.username);
});

socket.on('new_reaction', (data) => {
    showReactionAnimation(data);
    addSystemMessage(`${data.username} reacted with ${data.emoji} at ${formatTime(data.video_time)}`);
});

if (video) {
    enhanceVideoElement();
    
    video.addEventListener('error', (e) => {
        const errorCode = video.error ? video.error.code : 'unknown';
    });
    
    video.addEventListener('loadstart', () => {
        addSystemMessage('Loading video...');
    });
    
    video.addEventListener('canplay', () => {
        addSystemMessage('Video loaded successfully');
    });
    
    video.addEventListener('loadedmetadata', () => {
        if (video.duration && !isNaN(video.duration)) {
            addSystemMessage(`Video duration: ${formatTime(video.duration)}`);
        }
    });
    
    video.addEventListener('stalled', () => {
        addSystemMessage('Video loading stalled, please wait...');
    });
    
    video.addEventListener('waiting', () => {
        addSystemMessage('Buffering...');
    });
    
    video.addEventListener('play', () => {
        if (!isSyncing) {
            socket.emit('play', { time: video.currentTime });
        }
    });
    
    video.addEventListener('pause', () => {
        if (!isSyncing) {
            socket.emit('pause', { time: video.currentTime });
        }
    });
    
    video.addEventListener('seeked', () => {
        if (!isSyncing) {
            const currentTime = video.currentTime;
            if (Math.abs(currentTime - lastSeekTime) > 0.5) {
                clearTimeout(seekTimeout);
                seekTimeout = setTimeout(() => {
                    socket.emit('seek', { time: currentTime });
                    lastSeekTime = currentTime;
                }, 200);
            }
        }
    });
}

movieSelector.addEventListener('change', (e) => {
    if (e.target.value) {
        const selectedMovie = e.target.value;
        socket.emit('change_movie', { movie: selectedMovie });
    }
});

function toggleTheaterMode() {
    isTheaterMode = !isTheaterMode;
    document.body.classList.toggle('theater-mode', isTheaterMode);
    
    const theaterBtn = document.getElementById('theaterModeBtn');
    const theaterText = document.getElementById('theaterText');
    const theaterIcon = document.getElementById('theaterIcon');
    
    if (isTheaterMode) {
        theaterText.style.display = 'none';
        theaterIcon.textContent = '✕';
        theaterBtn.title = 'Exit Theater Mode';
    } else {
        theaterText.style.display = 'inline';
        theaterText.textContent = 'Theater Mode';
        theaterIcon.textContent = '🎭';
        theaterBtn.title = 'Theater Mode';
    }
}

function sendMessage() {
    const message = messageInput.value.trim();
    const spoiler = document.getElementById('spoilerCheckbox')?.checked;
    if (message) {
        socket.emit('send_message', { message: message, spoiler: spoiler });
        messageInput.value = '';
        if (document.getElementById('spoilerCheckbox')) document.getElementById('spoilerCheckbox').checked = false;
        stopTyping();
    }
}

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    } else {
        handleTyping();
    }
});

messageInput.addEventListener('input', handleTyping);

function handleTyping() {
    if (!isTyping) {
        isTyping = true;
        socket.emit('typing');
    }
    
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        stopTyping();
    }, 1000);
}

function stopTyping() {
    if (isTyping) {
        isTyping = false;
        socket.emit('stop_typing');
    }
    clearTimeout(typingTimeout);
}

function smartScroll() {
    if (autoScrollEnabled && !userScrolledUp) {
        requestAnimationFrame(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    }
}

if (chatMessages) {
    chatMessages.addEventListener('scroll', () => {
        const isAtBottom = chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight < 50;
        userScrolledUp = !isAtBottom;
        autoScrollEnabled = isAtBottom;
    });
}

function addMessage(username, message, timestamp, avatar, messageId, reactions = {}, scroll = true, spoiler = false) {
    const div = document.createElement('div');
    div.className = 'message';
    div.dataset.messageId = messageId;
    if (username === CURRENT_USERNAME) {
        div.classList.add('own-message');
    }
    let reactionsHtml = '';
    if (reactions && Object.keys(reactions).length > 0) {
        reactionsHtml = '<div class="message-reactions">';
        for (const [emoji, users] of Object.entries(reactions)) {
            const userReacted = users.includes(CURRENT_USERNAME);
            reactionsHtml += `<div class="reaction ${userReacted ? 'user-reacted' : ''}" onclick="reactToMessage('${messageId}', '${emoji}')">${emoji} ${users.length}</div>`;
        }
        reactionsHtml += '</div>';
    }
    let avatarHtml;
    if (avatar && avatar.startsWith('/avatars/')) {
        avatarHtml = `<img class="avatar" src="${avatar}" alt="${username}" onerror="this.style.display='none'">`;
    } else {
        avatarHtml = ``;
    }
    let messageContent;
    if (spoiler) {
        messageContent = `<span class='spoiler' tabindex='0' onclick='toggleSpoiler(this)' onkeydown='if(event.key==="Enter"||event.key===" "){toggleSpoiler(this);event.preventDefault();}'>${escapeHtml(message)}</span>`;
    } else {
        messageContent = escapeHtml(message);
    }
    div.innerHTML = `
        <button class="message-reactions-btn" onclick="showReactionPicker(this, '${messageId}')">+</button>
        ${avatarHtml}
        <span class="username">${username}</span>
        <span class="timestamp">${timestamp}</span>
        <div>${messageContent}</div>
        ${reactionsHtml}
        <div class="reaction-picker">
            <button onclick="reactToMessage('${messageId}', '❤️')">❤️</button>
            <button onclick="reactToMessage('${messageId}', '👍')">👍</button>
            <button onclick="reactToMessage('${messageId}', '👎')">👎</button>
            <button onclick="reactToMessage('${messageId}', '😮')">😮</button>
            <button onclick="reactToMessage('${messageId}', '😢')">😢</button>
        </div>
    `;
    chatMessages.appendChild(div);
    if (scroll) {
        smartScroll();
    }
}

function showTypingIndicator(username, avatar) {
}

function hideTypingIndicator(username) {
}

function addSystemMessage(message) {
    const div = document.createElement('div');
    div.className = 'message system';
    div.textContent = message;
    chatMessages.appendChild(div);
    
    smartScroll();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function updateUserList(users, count, userDetails, typingUsers = []) {
    document.getElementById('userCount').textContent = count;
    const onlineUsers = document.getElementById('onlineUsers');
    onlineUsers.innerHTML = '';
    
    users.forEach(username => {
        const userDiv = document.createElement('div');
        userDiv.className = 'user-badge';
        
        const userInfo = userDetails[username];
        if (userInfo) {
            let avatarHtml = '';
            if (userInfo.avatar && userInfo.avatar.startsWith('/avatars/')) {
                avatarHtml = `<img src="${userInfo.avatar}" alt="${username}" onerror="this.style.display='none'">`;
            }
            
            userDiv.innerHTML = `${avatarHtml}<span>${username}</span>`;
            if (userInfo.is_watching) {
                userDiv.classList.add('watching');
            }
            if (typingUsers.includes(username)) {
                userDiv.classList.add('typing');
            }
        } else {
            userDiv.innerHTML = `<span>${username}</span>`;
            if (typingUsers.includes(username)) {
                userDiv.classList.add('typing');
            }
        }
        
        onlineUsers.appendChild(userDiv);
    });
}

function sendReaction(emoji) {
    const videoTime = video ? video.currentTime : 0;
    socket.emit('send_reaction', {
        emoji: emoji,
        video_time: videoTime
    });
}

function showReactionAnimation(data) {
    const videoContainer = document.querySelector('.video-container');
    if (!videoContainer) return;
    
    const reactionDiv = document.createElement('div');
    reactionDiv.className = 'reaction-animation';
    reactionDiv.textContent = data.emoji;
    
    const containerRect = videoContainer.getBoundingClientRect();
    const containerWidth = videoContainer.offsetWidth;
    const containerHeight = videoContainer.offsetHeight;
    
    const padding = 50;
    const randomX = Math.random() * (containerWidth - padding * 2) + padding;
    const randomY = Math.random() * (containerHeight - padding * 2) + padding;
    
    reactionDiv.style.left = randomX + 'px';
    reactionDiv.style.top = randomY + 'px';
    
    videoContainer.appendChild(reactionDiv);
    
    setTimeout(() => {
        if (reactionDiv.parentNode) {
            reactionDiv.remove();
        }
    }, 2000);
}

function showReactionPicker(button, messageId) {
    document.querySelectorAll('.reaction-picker.show').forEach(picker => {
        if (picker !== button.parentElement.querySelector('.reaction-picker')) {
            picker.classList.remove('show');
        }
    });
    
    const picker = button.parentElement.querySelector('.reaction-picker');
    picker.classList.toggle('show');
    
    setTimeout(() => {
        document.addEventListener('click', function closeOnOutside(e) {
            if (!picker.contains(e.target) && !button.contains(e.target)) {
                picker.classList.remove('show');
                document.removeEventListener('click', closeOnOutside);
            }
        });
    }, 0);
}

function reactToMessage(messageId, emoji) {
    socket.emit('react_to_message', {
        message_id: messageId,
        emoji: emoji
    });
    
    document.querySelectorAll('.reaction-picker.show').forEach(picker => {
        picker.classList.remove('show');
    });
}

function updateMessageReactions(messageId, reactions) {
    const messageDiv = document.querySelector(`[data-message-id="${messageId}"]`);
    if (!messageDiv) return;
    
    let existingReactions = messageDiv.querySelector('.message-reactions');
    
    if (Object.keys(reactions).length === 0) {
        if (existingReactions) {
            existingReactions.remove();
        }
        return;
    }
    
    let reactionsHtml = '<div class="message-reactions">';
    for (const [emoji, users] of Object.entries(reactions)) {
        const userReacted = users.includes('{{ username }}');
        reactionsHtml += `<div class="reaction ${userReacted ? 'user-reacted' : ''}" onclick="reactToMessage('${messageId}', '${emoji}')">${emoji} ${users.length}</div>`;
    }
    reactionsHtml += '</div>';
    
    if (existingReactions) {
        existingReactions.outerHTML = reactionsHtml;
    } else {
        const picker = messageDiv.querySelector('.reaction-picker');
        picker.insertAdjacentHTML('beforebegin', reactionsHtml);
    }
}

function enhanceVideoElement() {
    const video = document.getElementById('videoPlayer');
    if (video) {
        video.setAttribute('preload', 'metadata');
        video.setAttribute('crossorigin', 'anonymous');
        video.setAttribute('controlsList', 'nodownload');
        
        video.removeAttribute('src');
        video.load();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (video) {
        enhanceVideoElement();
        
        setTimeout(() => {
            if (movieSelector.value) {
                enhanceVideoElement();
            }
        }, 500);
    }
});

function toggleSpoiler(el) {
    el.classList.toggle('revealed');
}