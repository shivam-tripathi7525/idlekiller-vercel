from flask import Flask, render_template, request, jsonify, session
import sqlite3
import time
import os

app = Flask(__name__, static_folder='../static', template_folder='../templates')
app.secret_key = 'your-secret-key'  # इसे strong रख!

# 📌 Database Setup (Auto-Create)
def init_db():
    conn = sqlite3.connect('idlekiller.db')
    c = conn.cursor()
    
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, 
        password TEXT, 
        is_admin INTEGER
    )''')

    # Chat Rooms Table
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        creator TEXT
    )''')

    # Messages Table
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        room_id INTEGER, 
        sender TEXT, 
        content TEXT, 
        timestamp INTEGER, 
        mode TEXT, 
        saved INTEGER DEFAULT 0
    )''')

    # Blogs Table
    c.execute('''CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        author TEXT, 
        content TEXT, 
        timestamp INTEGER
    )''')

    # Default Admin User
    c.execute('INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)', 
              ('admin', 'admin123', 1))

    conn.commit()
    conn.close()

init_db()

# 🏠 Home Route
@app.route('/')
def index():
    return render_template('index.html')

# 🔑 Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('idlekiller.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        session['username'] = username
        return jsonify({'status': 'success', 'username': username, 'is_admin': user[2]})
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

# 📝 Signup Route
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('idlekiller.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    if c.fetchone():
        conn.close()
        return jsonify({'status': 'error', 'message': 'Username already exists'}), 400

    c.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)', (username, password, 0))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'User created'})

# 🔥 Chat Rooms (Create & Fetch)
@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    conn = sqlite3.connect('idlekiller.db')
    c = conn.cursor()

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        room_name = data.get('room_name')
        c.execute('INSERT INTO rooms (name, creator) VALUES (?, ?)', (room_name, username))
        conn.commit()

    c.execute('SELECT * FROM rooms')
    rooms = [{'id': r[0], 'name': r[1], 'creator': r[2]} for r in c.fetchall()]
    conn.close()
    return jsonify(rooms)

# 💬 Fetch Messages for Room
@app.route('/messages/<int:room_id>', methods=['GET'])
def get_messages(room_id):
    conn = sqlite3.connect('idlekiller.db')
    c = conn.cursor()
    c.execute('SELECT * FROM messages WHERE room_id = ?', (room_id,))
    messages = [{'id': m[0], 'room_id': m[1], 'sender': m[2], 'content': m[3], 'timestamp': m[4], 'mode': m[5], 'saved': m[6]} 
                for m in c.fetchall()]
    conn.close()
    return jsonify(messages)

# 📨 Send Messages
@app.route('/messages', methods=['POST'])
def post_message():
    data = request.get_json()
    conn = sqlite3.connect('idlekiller.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (room_id, sender, content, timestamp, mode) VALUES (?, ?, ?, ?, ?)',
              (data['room_id'], data['sender'], data['content'], data['timestamp'], data['mode']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# 📝 Blog System
@app.route('/blogs', methods=['GET', 'POST'])
def blogs():
    conn = sqlite3.connect('idlekiller.db')
    c = conn.cursor()

    if request.method == 'POST':
        data = request.get_json()
        author = data.get('author')
        content = data.get('content')
        c.execute('INSERT INTO blogs (author, content, timestamp) VALUES (?, ?, ?)', 
                  (author, content, int(time.time() * 1000)))
        conn.commit()

    c.execute('SELECT * FROM blogs')
    blogs = [{'id': b[0], 'author': b[1], 'content': b[2], 'timestamp': b[3]} for b in c.fetchall()]
    conn.close()
    return jsonify(blogs)

# 🚀 Run Server with Gunicorn (Vercel Compatible)
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get('PORT', 5001)))
