#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Mini Server - เซิร์ฟเวอร์ขนาดเล็กที่ใช้งานง่าย (V1.2)
"""

from flask import Flask, request, jsonify, render_template_string
import requests
import os
import logging
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jarvis-mini-2025'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jarvis-mini")
_LAST_ERROR = None

# HTML Template แบบง่าย ๆ
MINI_TEMPLATE = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS AI Mini</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; color: white; }
        .container { max-width: 800px; margin: 0 auto; background: rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 30px; backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); }
        .header { text-align: center; margin-bottom: 30px; }
        .status { padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 5px solid #4CAF50; background: rgba(76, 175, 80, 0.2); }
        .chat-area { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 20px; margin: 20px 0; }
        .messages { height: 300px; overflow-y: auto; margin-bottom: 15px; padding: 15px; background: rgba(0, 0, 0, 0.2); border-radius: 10px; }
        .message { margin: 10px 0; padding: 10px 15px; border-radius: 15px; max-width: 80%; }
        .message.user { background: rgba(76, 175, 80, 0.3); margin-left: auto; text-align: right; }
        .message.ai { background: rgba(33, 150, 243, 0.3); margin-right: auto; }
        .input-area { display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 12px; border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 25px; background: rgba(255, 255, 255, 0.1); color: white; font-size: 16px; }
        .input-area input::placeholder { color: rgba(255, 255, 255, 0.7); }
        .btn { background: linear-gradient(45deg, #4CAF50, #45a049); color: white; border: none; padding: 12px 24px; border-radius: 25px; cursor: pointer; font-size: 16px; font-weight: 600; transition: all 0.3s ease; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 JARVIS AI Mini</h1>
            <p>เวอร์ชันขนาดเล็กที่ใช้งานง่าย</p>
        </div>

        <div class="status">
            <strong>✅ ระบบพร้อมใช้งาน!</strong><br>
            🔗 Ollama: {{ ollama_status }}<br>
            🧠 Models: {{ models }}<br>
            📅 เวลา: {{ current_time }}
        </div>

        <div class="chat-area">
            <h3>💬 แชทกับ JARVIS</h3>
            <div class="messages" id="messages">
                <div class="message ai">
                    สวัสดีครับ! ผม JARVIS AI Mini<br>
                    ทดลองถามอะไรผมได้นะครับ เช่น:<br>
                    • "สวัสดีครับ"<br>
                    • "วันนี้อากาศเป็นยังไง"<br>
                    • "เล่าเรื่องตลก"
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="พิมพ์ข้อความ..." onkeypress="handleEnter(event)">
                <button class="btn" onclick="sendMessage()" id="sendBtn">ส่ง</button>
            </div>
        </div>
    </div>

    <script>
        function addMessage(sender, content) {
            const messages = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            messageDiv.innerHTML = content;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            const message = input.value.trim();
            
            if (!message) return;

            addMessage('user', message);
            input.value = '';
            sendBtn.disabled = true;
            sendBtn.textContent = 'กำลังส่ง...';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });

                const result = await response.json();

                if (result.success) {
                    addMessage('ai', result.response);
                } else {
                    addMessage('ai', `❌ Error: ${result.message}`);
                }
            } catch (error) {
                addMessage('ai', `❌ เกิดข้อผิดพลาด: ${error.message}`);
            } finally {
                sendBtn.disabled = false;
                sendBtn.textContent = 'ส่ง';
            }
        }

        function handleEnter(event) {
            if (event.key === 'Enter') { sendMessage(); }
        }

        document.getElementById('messageInput').focus();
    </script>
</body>
</html>
"""

def _ollama_base_url():
    return os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

def check_ollama():
    try:
        r = requests.get(f"{_ollama_base_url()}/api/tags", timeout=(5, 10))
        if r.status_code == 200:
            data = r.json()
            models = [m['name'] for m in data.get('models', [])]
            return True, models
        return False, []
    except Exception as e:
        global _LAST_ERROR
        _LAST_ERROR = f"check_ollama: {e}"
        logger.warning(_LAST_ERROR)
        return False, []

def call_ollama(message: str):
    timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    connect_timeout = int(os.getenv("OLLAMA_CONNECT_TIMEOUT", "5"))
    max_retries = int(os.getenv("OLLAMA_RETRIES", "2"))
    base_url = _ollama_base_url()
    last_err = None

    payload = {
        "model": os.getenv("OLLAMA_MODEL", "phi3:mini"),
        "prompt": (
            "คุณคือ JARVIS AI ผู้ช่วยอัจฉริยะ ตอบเป็นภาษาไทยอย่างกระชับ ชัดเจน\n\n"
            f"คำถาม: {message}\nคำตอบ:"
        ),
        "stream": False
    }

    for attempt in range(max_retries + 1):
        try:
            logger.info(f"[Ollama] attempt={attempt+1}/{max_retries+1} model={payload['model']}")
            res = requests.post(
                f"{base_url}/api/generate",
                json=payload,
                timeout=(connect_timeout, timeout)
            )
            if res.status_code == 200:
                result = res.json()
                return result.get('response', 'ไม่สามารถสร้างคำตอบได้')
            else:
                last_err = f"Ollama API status {res.status_code}"
        except requests.exceptions.ReadTimeout:
            last_err = f"ขออภัย ระบบใช้เวลานานเกินไป (read timeout {timeout}s)"
        except requests.exceptions.RequestException as e:
            last_err = str(e)

        if attempt < max_retries:
            try:
                import time
                delay = 2 * (attempt + 1)
                logger.info(f"[Ollama] retrying in {delay}s... last_err={last_err}")
                time.sleep(delay)
            except Exception:
                pass

    global _LAST_ERROR
    _LAST_ERROR = last_err
    return (
        "ไม่สามารถติดต่อโมเดลได้ในขณะนี้: " + (last_err or "ไม่ทราบสาเหตุ") +
        "\nวิธีแก้ไข: ลองใหม่อีกครั้ง หรือเพิ่มเวลาได้ด้วยการตั้งค่า OLLAMA_TIMEOUT (เช่น 120)"
    )

@app.route('/')
def index():
    ok, models = check_ollama()
    return render_template_string(
        MINI_TEMPLATE,
        ollama_status="✅ ทำงานปกติ" if ok else "❌ ไม่พร้อม",
        models=", ".join(models) if models else "ไม่พบ models",
        current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        message = (data.get('message') or '').strip()
        if not message:
            return jsonify({'success': False, 'message': 'กรุณาใส่ข้อความ'})
        ai_response = call_ollama(message)
        return jsonify({'success': True, 'response': ai_response, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        global _LAST_ERROR
        _LAST_ERROR = f"/chat error: {e}"
        logger.exception(_LAST_ERROR)
        return jsonify({'success': False, 'message': str(e)})

@app.route('/health')
def health():
    ok, models = check_ollama()
    return jsonify({
        'status': 'ok',
        'ollama': ok,
        'models': models,
        'timestamp': datetime.now().isoformat(),
        'last_error': _LAST_ERROR
    })

@app.route('/config')
def config():
    return jsonify({
        'OLLAMA_HOST': _ollama_base_url(),
        'OLLAMA_MODEL': os.getenv('OLLAMA_MODEL', 'phi3:mini'),
        'OLLAMA_TIMEOUT': int(os.getenv('OLLAMA_TIMEOUT', '120')),
        'OLLAMA_CONNECT_TIMEOUT': int(os.getenv('OLLAMA_CONNECT_TIMEOUT', '5')),
        'OLLAMA_RETRIES': int(os.getenv('OLLAMA_RETRIES', '2'))
    })

@app.route('/api/models')
def list_models():
    ok, models = check_ollama()
    return jsonify({'success': ok, 'models': models})

if __name__ == '__main__':
    print("🚀 JARVIS AI Mini Server (V1.2)")
    print("📍 URL: http://localhost:5001")
    print("🔗 Ollama:", "✅ พร้อมใช้งาน" if check_ollama()[0] else "❌ ไม่พร้อม")
    app.run(host='0.0.0.0', port=5001, debug=True)
