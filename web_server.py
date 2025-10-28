# web_server.py - Flask Backend สำหรับ JARVIS Web Interface
"""
Flask server ที่เชื่อมต่อ HTML interface กับ AI Agent backend
รองรับ authentication, session management, และการจัดเก็บประวัติ
"""

from flask import Flask, request, jsonify, session, render_template_string, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import json
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
import logging
from ai_agent import LocalAIAgent

# สร้าง Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

# เปิดใช้ CORS และ SocketIO
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# กำหนดค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebJARVIS:
    def __init__(self):
        self.ai_agent = LocalAIAgent()
        self.init_database()
        self.active_sessions = {}
        
    def init_database(self):
        """สร้างฐานข้อมูลสำหรับ web interface"""
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        
        # ตาราง users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active INTEGER DEFAULT 1,
                settings TEXT DEFAULT '{}'
            )
        ''')
        
        # ตาราง conversations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                message_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # ตาราง messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                sender TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # ตาราง user_sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # สร้าง admin user ถ้าไม่มี
        self.create_default_admin()
    
    def create_default_admin(self):
        """สร้าง admin user เริ่มต้น"""
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            password_hash = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, created_at, settings)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'admin',
                password_hash,
                'admin@jarvis.local',
                datetime.now().isoformat(),
                json.dumps({'theme': 'dark', 'language': 'th'})
            ))
            conn.commit()
            logger.info("✅ สร้าง admin user เริ่มต้น (username: admin, password: admin123)")
        
        conn.close()
    
    def hash_password(self, password):
        """เข้ารหัสรหัสผ่าน"""
        return hashlib.sha256(f"{password}JARVIS_SALT".encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """ตรวจสอบรหัสผ่าน"""
        return self.hash_password(password) == password_hash
    
    def authenticate_user(self, username, password):
        """ตรวจสอบการล็อกอิน"""
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash, is_active FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and user[2] == 1 and self.verify_password(password, user[1]):
            # อัปเดต last_login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                         (datetime.now().isoformat(), user[0]))
            conn.commit()
            conn.close()
            return user[0]  # return user_id
        
        conn.close()
        return None
    
    def create_session(self, user_id, ip_address, user_agent):
        """สร้าง session ใหม่"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_sessions (id, user_id, created_at, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            user_id,
            datetime.now().isoformat(),
            expires_at.isoformat(),
            ip_address,
            user_agent
        ))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id):
        """ตรวจสอบ session"""
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, expires_at FROM user_sessions 
            WHERE id = ? AND is_active = 1
        ''', (session_id,))
        
        session_data = cursor.fetchone()
        conn.close()
        
        if session_data:
            expires_at = datetime.fromisoformat(session_data[1])
            if datetime.now() < expires_at:
                return session_data[0]  # return user_id
        
        return None
    
    def get_user_conversations(self, user_id, limit=50):
        """ดึงประวัติการสนทนา"""
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.title, c.created_at, c.updated_at, c.message_count,
                   m.content as last_message
            FROM conversations c
            LEFT JOIN (
                SELECT conversation_id, content,
                       ROW_NUMBER() OVER (PARTITION BY conversation_id ORDER BY timestamp DESC) as rn
                FROM messages
                WHERE sender = 'user'
            ) m ON c.id = m.conversation_id AND m.rn = 1
            WHERE c.user_id = ? 
            ORDER BY c.updated_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'id': row[0],
                'title': row[1] or 'บทสนทนาใหม่',
                'created_at': row[2],
                'updated_at': row[3],
                'message_count': row[4] or 0,
                'last_message': row[5] or 'ยังไม่มีข้อความ'
            })
        
        conn.close()
        return conversations
    
    def get_conversation_messages(self, conversation_id, user_id):
        """ดึงข้อความในการสนทนา"""
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        
        # ตรวจสอบว่า user เป็นเจ้าของการสนทนานี้
        cursor.execute('SELECT user_id FROM conversations WHERE id = ?', (conversation_id,))
        conv = cursor.fetchone()
        if not conv or conv[0] != user_id:
            conn.close()
            return []
        
        cursor.execute('''
            SELECT sender, content, timestamp, message_type, metadata
            FROM messages 
            WHERE conversation_id = ? 
            ORDER BY timestamp ASC
        ''', (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'sender': row[0],
                'content': row[1],
                'timestamp': row[2],
                'type': row[3],
                'metadata': json.loads(row[4])
            })
        
        conn.close()
        return messages
    
    def save_message(self, conversation_id, sender, content, message_type='text', metadata=None):
        """บันทึกข้อความ"""
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata or {})
        
        cursor.execute('''
            INSERT INTO messages (conversation_id, sender, content, timestamp, message_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (conversation_id, sender, content, timestamp, message_type, metadata_json))
        
        # อัปเดต conversation
        cursor.execute('''
            UPDATE conversations 
            SET updated_at = ?, message_count = message_count + 1
            WHERE id = ?
        ''', (timestamp, conversation_id))
        
        conn.commit()
        conn.close()
        
        return timestamp
    
    def create_conversation(self, user_id, title="แชทใหม่"):
        """สร้างการสนทนาใหม่"""
        conversation_id = f"conv_{int(datetime.now().timestamp() * 1000)}"
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations (id, user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (conversation_id, user_id, title, timestamp, timestamp))
        
        conn.commit()
        conn.close()
        
        return conversation_id

# สร้าง instance
web_jarvis = WebJARVIS()

# Routes
@app.route('/')
def index():
    """หน้าแรก - test page"""
    # ให้หน้าแรกเสิร์ฟ unified UI ที่รวม Login + Chat
    return send_from_directory('.', 'jarvis_unified.html')

@app.route('/register-page')
def register_page():
    """หน้า Register แยกต่างหาก"""
    return send_from_directory('.', 'register.html')

@app.route('/health')
def health():
    """ตรวจสอบสถานะระบบแบบง่าย"""
    status = {
        'status': 'ok',
        'time': datetime.now().isoformat(),
        'ollama': web_jarvis.ai_agent.check_ollama_status(),
        'models': web_jarvis.ai_agent.available_models,
        'db': None,
    }
    try:
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        status['db'] = {'connected': True, 'users': users_count}
        conn.close()
    except Exception as e:
        status['db'] = {'connected': False, 'error': str(e)}
    return jsonify(status)

@app.route('/config')
def config_info():
    """ดูค่าคอนฟิกสำคัญของระบบ"""
    base = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    return jsonify({
        'OLLAMA_HOST': base,
        'DEFAULT_MODEL': web_jarvis.ai_agent.default_model,
        'TIMEOUT': web_jarvis.ai_agent.ollama_timeout,
        'RETRIES': web_jarvis.ai_agent.ollama_retries,
    })

@app.route('/login', methods=['POST'])
def login():
    """API สำหรับล็อกอิน"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'กรุณากรอกข้อมูลให้ครบถ้วน'}), 400
    
    user_id = web_jarvis.authenticate_user(username, password)
    if user_id:
        session_id = web_jarvis.create_session(
            user_id, 
            request.remote_addr, 
            request.headers.get('User-Agent')
        )
        
        response = jsonify({
            'success': True,
            'message': 'เข้าสู่ระบบสำเร็จ',
            'user_id': user_id,
            'session_id': session_id
        })
        response.set_cookie('jarvis_session', session_id, max_age=86400)  # 24 hours
        return response
    else:
        return jsonify({'success': False, 'message': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'}), 401

@app.route('/register', methods=['POST'])
def register():
    """API สำหรับสมัครสมาชิกใหม่"""
    data = request.get_json()
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    email = (data.get('email') or '').strip() if data else ''

    if not username or not password:
        return jsonify({'success': False, 'message': 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน'}), 400

    try:
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        # ตรวจซ้ำ
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'ชื่อผู้ใช้ถูกใช้งานแล้ว'}), 409

        password_hash = web_jarvis.hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, created_at, settings)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            username,
            password_hash,
            email or None,
            datetime.now().isoformat(),
            json.dumps({'theme': 'dark', 'language': 'th'})
        ))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'สมัครสมาชิกสำเร็จ'}), 201
    except Exception as e:
        logger.error(f"Register error: {e}")
        return jsonify({'success': False, 'message': 'ไม่สามารถสมัครสมาชิกได้ กรุณาลองใหม่'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """API สำหรับออกจากระบบ"""
    session_id = request.cookies.get('jarvis_session')
    if session_id:
        conn = sqlite3.connect('jarvis_web.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE user_sessions SET is_active = 0 WHERE id = ?', (session_id,))
        conn.commit()
        conn.close()
    
    response = jsonify({'success': True, 'message': 'ออกจากระบบแล้ว'})
    response.set_cookie('jarvis_session', '', expires=0)
    return response

@app.route('/api/conversations')
def get_conversations():
    """ดึงรายการการสนทนา"""
    session_id = request.args.get('session_id') or request.cookies.get('jarvis_session')
    user_id = web_jarvis.validate_session(session_id)
    
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    conversations = web_jarvis.get_user_conversations(user_id)
    return jsonify({'success': True, 'conversations': conversations})

@app.route('/api/conversation/<conversation_id>')
def get_conversation(conversation_id):
    """ดึงข้อมูลบทสนทนาเดี่ยวและข้อความ"""
    session_id = request.args.get('session_id') or request.cookies.get('jarvis_session')
    user_id = web_jarvis.validate_session(session_id)
    
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    messages = web_jarvis.get_conversation_messages(conversation_id, user_id)
    return jsonify({'success': True, 'messages': messages})

@app.route('/api/conversations/<conversation_id>/messages')
def get_messages(conversation_id):
    """ดึงข้อความในการสนทนา"""
    session_id = request.args.get('session_id') or request.cookies.get('jarvis_session')
    user_id = web_jarvis.validate_session(session_id)
    
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    messages = web_jarvis.get_conversation_messages(conversation_id, user_id)
    return jsonify({'success': True, 'messages': messages})

@app.route('/api/chat', methods=['POST'])
def chat():
    """API สำหรับส่งข้อความและรับคำตอบจาก AI"""
    data = request.get_json()
    session_id = data.get('session_id') or request.cookies.get('jarvis_session')
    user_id = web_jarvis.validate_session(session_id)
    
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    message = data.get('message')
    conversation_id = data.get('conversation_id')
    
    if not message:
        return jsonify({'success': False, 'message': 'Message is required'}), 400
    
    # สร้างการสนทนาใหม่ถ้าไม่มี
    if not conversation_id:
        conversation_id = web_jarvis.create_conversation(user_id)
    
    # บันทึกข้อความของผู้ใช้
    user_timestamp = web_jarvis.save_message(conversation_id, 'user', message)
    
    # ส่งไปยัง AI Agent
    try:
        ai_result = web_jarvis.ai_agent.process_request(message)
        ai_response = ai_result['ai_response']
        
        # บันทึกคำตอบของ AI
        ai_metadata = {
            'model_used': ai_result.get('model_used'),
            'processing_time': ai_result.get('processing_time'),
            'platform_detected': ai_result.get('platform_detected'),
            'internet_data': bool(ai_result.get('internet_data'))
        }
        
        ai_timestamp = web_jarvis.save_message(
            conversation_id, 'ai', ai_response, 'text', ai_metadata
        )
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'conversation_id': conversation_id,
            'timestamp': ai_timestamp,
            'metadata': ai_metadata
        })
        
    except Exception as e:
        logger.error(f"AI processing error: {e}")
        return jsonify({'success': False, 'message': 'เกิดข้อผิดพลาดในการประมวลผล AI'}), 500

# Socket.IO Events
@socketio.on('connect')
def handle_connect(auth=None):
    """เมื่อมีการเชื่อมต่อ WebSocket"""
    # รองรับทั้งคุกกี้และ auth payload จาก client
    session_id = request.cookies.get('jarvis_session') or (auth.get('session_id') if isinstance(auth, dict) else None)
    user_id = web_jarvis.validate_session(session_id)
    
    if user_id:
        join_room(f"user_{user_id}")
        emit('connected', {'message': 'เชื่อมต่อสำเร็จ'})
        logger.info(f"User {user_id} connected via WebSocket")
    else:
        emit('error', {'message': 'การตรวจสอบสิทธิ์ล้มเหลว'})

@socketio.on('disconnect')
def handle_disconnect():
    """เมื่อมีการตัดการเชื่อมต่อ"""
    logger.info("User disconnected")

@socketio.on('send_message')
def handle_send_message(data):
    """รับข้อความผ่าน WebSocket"""
    session_id = request.cookies.get('jarvis_session')
    user_id = web_jarvis.validate_session(session_id)
    
    if not user_id:
        emit('error', {'message': 'Unauthorized'})
        return
    
    message = data.get('message')
    conversation_id = data.get('conversation_id')
    
    if not message:
        emit('error', {'message': 'Message is required'})
        return
    
    # สร้างการสนทนาใหม่ถ้าไม่มี
    if not conversation_id:
        conversation_id = web_jarvis.create_conversation(user_id)
    
    # บันทึกข้อความของผู้ใช้
    user_timestamp = web_jarvis.save_message(conversation_id, 'user', message)
    
    # แสดง typing indicator
    emit('ai_typing', {'conversation_id': conversation_id})
    
    try:
        # ส่งไปยัง AI Agent
        ai_result = web_jarvis.ai_agent.process_request(message)
        ai_response = ai_result['ai_response']
        
        # บันทึกคำตอบของ AI
        ai_metadata = {
            'model_used': ai_result.get('model_used'),
            'processing_time': ai_result.get('processing_time'),
            'platform_detected': ai_result.get('platform_detected'),
            'internet_data': bool(ai_result.get('internet_data'))
        }
        
        ai_timestamp = web_jarvis.save_message(
            conversation_id, 'ai', ai_response, 'text', ai_metadata
        )
        
        # ส่งคำตอบกลับ
        emit('ai_response', {
            'conversation_id': conversation_id,
            'message': ai_response,
            'timestamp': ai_timestamp,
            'metadata': ai_metadata
        })
        
    except Exception as e:
        logger.error(f"AI processing error: {e}")
        emit('error', {'message': 'เกิดข้อผิดพลาดในการประมวลผล AI'})

if __name__ == '__main__':
    print("🚀 เริ่มต้น JARVIS Web Server")
    print("📍 URL: http://localhost:5000")
    print("👤 Admin Login: admin / admin123")
    print("💾 Database: jarvis_web.db")
    
    # รัน server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)