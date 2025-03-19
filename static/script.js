let currentUser = null;
let isAdmin = false;
let currentRoomId = null;
let isProfessionalMode = false;

document.getElementById('login-btn').addEventListener('click', async () => {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (data.status === 'success') {
        currentUser = data.username;
        isAdmin = data.is_admin;
        document.getElementById('auth-page').style.display = 'none';
        document.getElementById('app-container').style.display = 'block';
        document.getElementById('room-container').style.display = 'flex';
        document.getElementById('room-create').style.display = isAdmin ? 'flex' : 'none';
        document.getElementById('room-header-title').textContent = isAdmin ? 'Select or Create a Room' : 'Select a Room';
        loadRooms();
    } else {
        alert(data.message);
    }
});

// Signup, logout, aur baaki functions same reh sakte hain...

async function loadRooms() {
    const response = await fetch('/rooms');
    const rooms = await response.json();
    const roomList = document.getElementById('room-list');
    roomList.innerHTML = '';
    rooms.forEach(room => {
        const div = document.createElement('div');
        div.classList.add('room-item');
        div.textContent = `${room.name} (Created by ${room.creator})`;
        div.addEventListener('click', () => enterRoom(room.id, room.name));
        roomList.appendChild(div);
    });
}

document.getElementById('create-room-btn').addEventListener('click', async () => {
    const roomName = document.getElementById('room-name').value.trim();
    if (roomName && isAdmin) {
        const response = await fetch('/rooms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser, room_name: roomName })
        });
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('room-name').value = '';
            loadRooms();
        } else {
            alert(data.message);
        }
    }
});

async function enterRoom(roomId, roomName) {
    currentRoomId = roomId;
    document.getElementById('room-container').style.display = 'none';
    document.getElementById('chat-container').style.display = 'flex';
    document.getElementById('chat-room-name').textContent = roomName;
    loadMessages();
    setInterval(loadMessages, 2000); // Polling every 2 seconds
}

async function loadMessages() {
    const response = await fetch(`/messages/${currentRoomId}`);
    const messages = await response.json();
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    messages.forEach(msg => {
        const p = document.createElement('p');
        p.classList.add(msg.sender === currentUser ? 'me' : 'friend');
        p.setAttribute('data-mode', msg.mode);
        p.textContent = `${msg.content} (${new Date(msg.timestamp).toLocaleTimeString()})`;
        chatMessages.appendChild(p);
    });
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

document.getElementById('send-btn').addEventListener('click', async () => {
    const message = document.getElementById('message-input').value.trim();
    if (message && currentUser && currentRoomId) {
        const msg = { room_id: currentRoomId, sender: currentUser, content: message, timestamp: Date.now(), mode: isProfessionalMode ? 'professional' : 'personal' };
        const response = await fetch('/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(msg)
        });
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('message-input').value = '';
            loadMessages();
        }
    }
});

// Baaki code (emoji, blogs, etc.) same reh sakta hai...
