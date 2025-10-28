import requests
import json
import sqlite3
import threading
from datetime import datetime
import logging
import re
import time
from typing import Optional, Dict, List
import os

class LocalAIAgent:
    def __init__(self):
        base = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        self.ollama_url = f"{base}/api/generate"
        self.ollama_tags_url = f"{base}/api/tags"
        self.default_model = "phi3:mini"  # รองรับ Phi-3 mini เป็น default
        self.available_models = []
        self.ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", "120"))
        self.ollama_retries = int(os.getenv("OLLAMA_RETRIES", "2"))
        self.setup_database()
        self.setup_logging()
        self.check_ollama_status()
        self.load_available_models()
    
    def setup_database(self):
        """สร้างฐานข้อมูล SQLite สำหรับบันทึกการทำงาน"""
        # อนุญาตใช้งานข้ามเธรด และล็อกเพื่อความปลอดภัย
        self.conn = sqlite3.connect('ai_agent_logs.db', check_same_thread=False)
        self.db_lock = threading.Lock()
        cursor = self.conn.cursor()
        
        # Table หลักสำหรับ logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_input TEXT,
                ai_response TEXT,
                model_used TEXT,
                action_taken TEXT,
                internet_data TEXT,
                response_time REAL,
                success INTEGER DEFAULT 1
            )
        ''')
        
        # Table สำหรับ internet activities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS internet_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                platform TEXT,
                query TEXT,
                response_data TEXT,
                success INTEGER DEFAULT 1,
                agent_log_id INTEGER,
                FOREIGN KEY (agent_log_id) REFERENCES agent_logs (id)
            )
        ''')
        
        # Table สำหรับ model performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                total_requests INTEGER DEFAULT 0,
                avg_response_time REAL DEFAULT 0,
                success_rate REAL DEFAULT 100,
                last_updated TEXT
            )
        ''')
        
        self.conn.commit()
    
    def setup_logging(self):
        """ตั้งค่าระบบบันทึก log"""
        logging.basicConfig(
            filename='agent_activity.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def check_ollama_status(self):
        """ตรวจสอบสถานะ Ollama และความพร้อมใช้งาน"""
        try:
            response = requests.get(self.ollama_tags_url, timeout=10)
            if response.status_code == 200:
                logging.info("✅ Ollama is running and accessible")
                return True
            else:
                logging.warning(f"⚠️ Ollama responded with status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Cannot connect to Ollama: {e}")
            return False
    
    def load_available_models(self):
        """โหลดรายชื่อโมเดลที่มีใช้งานได้"""
        try:
            response = requests.get(self.ollama_tags_url, timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['name'] for model in models_data.get('models', [])]
                logging.info(f"📦 Available models: {self.available_models}")
                
                # ตรวจสอบว่ามี phi3:mini หรือไม่
                if self.default_model not in self.available_models:
                    if self.available_models:
                        self.default_model = self.available_models[0]
                        logging.info(f"🔄 Using fallback model: {self.default_model}")
                    else:
                        logging.error("❌ No models available!")
        except Exception as e:
            logging.error(f"❌ Failed to load models: {e}")
            self.available_models = []
    
    def call_ollama(self, prompt, model=None):
        """เรียกใช้โมเดล AI ผ่าน Ollama (เพิ่ม timeout และ retry)"""
        start_time = time.time()
        model_to_use = model or self.default_model
        last_err = None

        payload = {
            "model": model_to_use,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40
            }
        }

        for attempt in range(self.ollama_retries + 1):
            try:
                response = requests.post(self.ollama_url, json=payload, timeout=self.ollama_timeout)
                response_time = time.time() - start_time

                if response.status_code == 200:
                    result = response.json().get('response', 'No response')
                    self.update_model_performance(model_to_use, response_time, True)
                    return result
                else:
                    last_err = f"API status {response.status_code}"
                    self.update_model_performance(model_to_use, response_time, False)
            except requests.exceptions.ReadTimeout:
                last_err = f"Read timeout after {self.ollama_timeout}s"
                response_time = time.time() - start_time
                self.update_model_performance(model_to_use, response_time, False)
            except requests.exceptions.RequestException as e:
                last_err = str(e)
                response_time = time.time() - start_time
                self.update_model_performance(model_to_use, response_time, False)

            if attempt < self.ollama_retries:
                try:
                    time.sleep(2 * (attempt + 1))
                except Exception:
                    pass

        logging.error(f"Ollama call failed after retries: {last_err}")
        return f"Error: Ollama not responding ({last_err}). โปรดลองอีกครั้งภายหลัง หรือเพิ่ม OLLAMA_TIMEOUT."
    
    def update_model_performance(self, model_name, response_time, success):
        """อัปเดตสถิติประสิทธิภาพของโมเดล"""
        with self.db_lock:
            cursor = self.conn.cursor()
        
        # ดึงข้อมูลปัจจุบัน
        cursor.execute('SELECT * FROM model_performance WHERE model_name = ?', (model_name,))
        existing = cursor.fetchone()
        
        if existing:
            total_requests = existing[2] + 1
            current_avg = existing[3]
            new_avg = ((current_avg * existing[2]) + response_time) / total_requests
            current_success_rate = existing[4]
            new_success_rate = ((current_success_rate * existing[2]) + (100 if success else 0)) / total_requests
            
            cursor.execute('''
                UPDATE model_performance 
                SET total_requests = ?, avg_response_time = ?, success_rate = ?, last_updated = ?
                WHERE model_name = ?
            ''', (total_requests, new_avg, new_success_rate, datetime.now().isoformat(), model_name))
        else:
            cursor.execute('''
                INSERT INTO model_performance (model_name, total_requests, avg_response_time, success_rate, last_updated)
                VALUES (?, 1, ?, ?, ?)
            ''', (model_name, response_time, 100 if success else 0, datetime.now().isoformat()))
        
            self.conn.commit()
    
    def fetch_internet_data(self, query, platform="general"):
        """ดึงข้อมูลจากอินเทอร์เน็ตจากแพลตฟอร์มต่าง ๆ"""
        try:
            if platform.lower() == "reddit":
                return self.fetch_reddit_data(query)
            elif platform.lower() == "youtube":
                return self.fetch_youtube_data(query)
            elif platform.lower() == "facebook":
                return self.fetch_facebook_data(query)
            elif platform.lower() == "weather":
                return self.fetch_weather_data(query)
            else:
                return self.fetch_general_data(query)
        except Exception as e:
            logging.error(f"Internet fetch error: {e}")
            return {"error": str(e), "platform": platform}
    
    def fetch_reddit_data(self, query):
        """ดึงข้อมูลจาก Reddit (ใช้ Reddit API หรือ RSS feeds)"""
        try:
            # ใช้ Reddit RSS feed สำหรับการค้นหาพื้นฐาน
            url = f"https://www.reddit.com/search.json?q={query}&limit=5"
            headers = {'User-Agent': 'JARVIS-AI-Agent/1.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = []
                for post in data.get('data', {}).get('children', []):
                    post_data = post.get('data', {})
                    posts.append({
                        'title': post_data.get('title', ''),
                        'url': post_data.get('url', ''),
                        'score': post_data.get('score', 0),
                        'subreddit': post_data.get('subreddit', ''),
                        'created_utc': post_data.get('created_utc', 0)
                    })
                return {'platform': 'reddit', 'posts': posts, 'query': query}
            else:
                return {'platform': 'reddit', 'error': f'HTTP {response.status_code}', 'query': query}
        except Exception as e:
            return {'platform': 'reddit', 'error': str(e), 'query': query}
    
    def fetch_youtube_data(self, query):
        """ดึงข้อมูลจาก YouTube (ต้องมี API key สำหรับการใช้งานเต็มรูปแบบ)"""
        try:
            # สำหรับ demo ใช้ search simulation
            # ในการใช้งานจริงต้องใช้ YouTube Data API v3
            youtube_data = {
                'platform': 'youtube',
                'query': query,
                'note': 'YouTube API requires authentication key',
                'suggested_videos': [
                    f"How to {query}",
                    f"{query} tutorial",
                    f"{query} explained",
                    f"Best {query} examples"
                ]
            }
            
            # ถ้ามี API key สามารถใช้โค้ดนี้:
            # api_key = "YOUR_YOUTUBE_API_KEY"
            # url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={api_key}"
            # response = requests.get(url)
            
            return youtube_data
        except Exception as e:
            return {'platform': 'youtube', 'error': str(e), 'query': query}
    
    def fetch_facebook_data(self, query):
        """ดึงข้อมูลจาก Facebook (ต้องมี access token)"""
        try:
            # Facebook Graph API ต้องมี access token
            facebook_data = {
                'platform': 'facebook',
                'query': query,
                'note': 'Facebook API requires access token and app permissions',
                'status': 'API authentication required'
            }
            
            # ถ้ามี access token สามารถใช้โค้ดนี้:
            # access_token = "YOUR_FACEBOOK_ACCESS_TOKEN"
            # url = f"https://graph.facebook.com/v18.0/search?q={query}&type=post&access_token={access_token}"
            # response = requests.get(url)
            
            return facebook_data
        except Exception as e:
            return {'platform': 'facebook', 'error': str(e), 'query': query}
    
    def fetch_weather_data(self, location="Bangkok"):
        """ดึงข้อมูลสภาพอากาศ (ใช้ free weather API)"""
        try:
            # ใช้ OpenWeatherMap free tier หรือ wttr.in
            url = f"https://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                weather_data = response.json()
                current = weather_data.get('current_condition', [{}])[0]
                return {
                    'platform': 'weather',
                    'location': location,
                    'temperature': current.get('temp_C', 'N/A'),
                    'description': current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
                    'humidity': current.get('humidity', 'N/A'),
                    'wind_speed': current.get('windspeedKmph', 'N/A'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'platform': 'weather', 'error': f'HTTP {response.status_code}', 'location': location}
        except Exception as e:
            return {'platform': 'weather', 'error': str(e), 'location': location}
    
    def fetch_general_data(self, query):
        """ดึงข้อมูลทั่วไป (ใช้ JSONPlaceholder หรือ public APIs)"""
        try:
            # ตัวอย่างการดึงข้อมูลจาก API สาธารณะ
            response = requests.get(f"https://jsonplaceholder.typicode.com/posts?title_like={query}", timeout=10)
            if response.status_code == 200:
                return {
                    'platform': 'general',
                    'data': response.json(),
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'platform': 'general', 'error': f'HTTP {response.status_code}', 'query': query}
        except Exception as e:
            return {'platform': 'general', 'error': str(e), 'query': query}
    
    def process_request(self, user_input, preferred_model=None):
        """ประมวลผลคำขอจากผู้ใช้ (ป้องกัน error กระทบบริการ)"""
        start_time = time.time()
        try:
            # วิเคราะห์ intent จาก user input
            platform, query = self.analyze_intent(user_input)

            # เรียกใช้ AI
            ai_response = self.call_ollama(user_input, preferred_model)

            # ดึงข้อมูลจากอินเทอร์เน็ตถ้าจำเป็น
            internet_data = None
            if platform:
                try:
                    internet_data = self.fetch_internet_data(query, platform)
                    # บันทึกกิจกรรมอินเทอร์เน็ตแบบ best-effort
                    try:
                        self.log_internet_activity(platform, query, internet_data)
                    except Exception as e:
                        logging.warning(f"Skip logging internet activity: {e}")
                except Exception as e:
                    logging.error(f"Internet fetch failed: {e}")
                    internet_data = {"error": str(e), "platform": platform}

            processing_time = time.time() - start_time
            model_used = preferred_model or self.default_model

            # บันทึกผลลัพธ์
            try:
                log_id = self.log_to_db(
                    user_input, ai_response, model_used,
                    str(internet_data) if internet_data else None,
                    processing_time
                )
            except Exception as e:
                logging.warning(f"Skip DB log due to: {e}")
                log_id = None

            return {
                "ai_response": ai_response,
                "internet_data": internet_data,
                "model_used": model_used,
                "processing_time": round(processing_time, 2),
                "platform_detected": platform,
                "timestamp": datetime.now().isoformat(),
                "log_id": log_id
            }
        except Exception as e:
            # ป้องกันไม่ให้ backend พัง ส่งข้อความแสดงข้อผิดพลาดแบบสุภาพกลับไปแทน
            logging.error(f"process_request failed: {e}")
            processing_time = time.time() - start_time
            return {
                "ai_response": f"ขออภัย ระบบเกิดข้อผิดพลาดระหว่างประมวลผล ({e})",
                "internet_data": None,
                "model_used": preferred_model or self.default_model,
                "processing_time": round(processing_time, 2),
                "platform_detected": None,
                "timestamp": datetime.now().isoformat(),
                "log_id": None
            }
    
    def analyze_intent(self, user_input):
        """วิเคราะห์ความตั้งใจของผู้ใช้เพื่อกำหนด platform และ query"""
        text = user_input.lower()
        
        # ตรวจหา platform keywords
        if any(keyword in text for keyword in ['reddit', 'r/', 'subreddit']):
            # แยก query จาก reddit keywords
            query = re.sub(r'\b(reddit|r/|subreddit)\b', '', text).strip()
            return 'reddit', query or user_input
            
        elif any(keyword in text for keyword in ['youtube', 'yt', 'video', 'วิดีโอ']):
            query = re.sub(r'\b(youtube|yt|video|วิดีโอ)\b', '', text).strip()
            return 'youtube', query or user_input
            
        elif any(keyword in text for keyword in ['facebook', 'fb', 'เฟซบุ๊ก']):
            query = re.sub(r'\b(facebook|fb|เฟซบุ๊ก)\b', '', text).strip()
            return 'facebook', query or user_input
            
        elif any(keyword in text for keyword in ['weather', 'อากาศ', 'สภาพอากาศ', 'อุณหภูมิ']):
            # หา location ถ้ามี
            location_match = re.search(r'(?:ที่|ใน|at|in)\s+(\w+)', text)
            location = location_match.group(1) if location_match else 'Bangkok'
            return 'weather', location
            
        elif any(keyword in text for keyword in ['ข้อมูล', 'ข่าว', 'ค้นหา', 'search', 'news', 'data']):
            return 'general', user_input
            
        return None, user_input
    
    def log_to_db(self, user_input, response, model_used, internet_data=None, response_time=0):
        """บันทึกการทำงานลงฐานข้อมูล"""
        with self.db_lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO agent_logs (timestamp, user_input, ai_response, model_used, action_taken, internet_data, response_time, success)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(), 
                user_input, 
                response, 
                model_used,
                "processed", 
                internet_data,
                response_time,
                1 if not response.startswith("Error:") else 0
            ))
            log_id = cursor.lastrowid
            self.conn.commit()
        
        # บันทึก log file
        logging.info(f"User: {user_input[:100]}... | Model: {model_used} | Time: {response_time:.2f}s")
        return log_id
    
    def log_internet_activity(self, platform, query, response_data):
        """บันทึกกิจกรรมการเชื่อมต่ออินเทอร์เน็ต"""
        with self.db_lock:
            cursor = self.conn.cursor()
            success = 1 if 'error' not in str(response_data) else 0
            cursor.execute('''
                INSERT INTO internet_logs (timestamp, platform, query, response_data, success)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                platform,
                query,
                json.dumps(response_data, ensure_ascii=False),
                success
            ))
            internet_log_id = cursor.lastrowid
            self.conn.commit()
            return internet_log_id
    
    def get_statistics(self):
        """ดึงสถิติการใช้งาน"""
        with self.db_lock:
            cursor = self.conn.cursor()
            # สถิติโดยรวม
            cursor.execute('SELECT COUNT(*), AVG(response_time), AVG(success) FROM agent_logs')
            overall_stats = cursor.fetchone()

            # สถิติต่อโมเดล
            cursor.execute('''
                SELECT model_used, COUNT(*), AVG(response_time), AVG(success) 
                FROM agent_logs 
                GROUP BY model_used
            ''')
            model_stats = cursor.fetchall()

            # สถิติ internet activities
            cursor.execute('''
                SELECT platform, COUNT(*), AVG(success) 
                FROM internet_logs 
                GROUP BY platform
            ''')
            internet_stats = cursor.fetchall()

        return {
            'overall': {
                'total_requests': overall_stats[0],
                'avg_response_time': round(overall_stats[1] or 0, 2),
                'success_rate': round((overall_stats[2] or 0) * 100, 1)
            },
            'by_model': [
                {
                    'model': stat[0],
                    'requests': stat[1],
                    'avg_time': round(stat[2], 2),
                    'success_rate': round(stat[3] * 100, 1)
                } for stat in model_stats
            ],
            'internet_usage': [
                {
                    'platform': stat[0],
                    'requests': stat[1],
                    'success_rate': round(stat[2] * 100, 1)
                } for stat in internet_stats
            ]
        }

# Helper functions for external usage
def get_agent_instance():
    """สร้าง instance ของ LocalAIAgent"""
    return LocalAIAgent()

# ใช้งาน Agent
if __name__ == "__main__":
    agent = LocalAIAgent()
    
    # ตัวอย่างการใช้งาน
    test_queries = [
        "สวัสดี จากโมเดล Phi-3",
        "ค้นหาข้อมูลใน reddit เกี่ยวกับ AI",
        "ดูสภาพอากาศที่กรุงเทพ",
        "หาวิดีโอใน youtube เกี่ยวกับ Python"
    ]
    
    for query in test_queries:
        print(f"\n🔄 Processing: {query}")
        result = agent.process_request(query)
        print(f"📝 Response: {result['ai_response'][:100]}...")
        if result.get('internet_data'):
            print(f"🌐 Internet data: {result['platform_detected']}")
    
    # แสดงสถิติ
    print("\n📊 Statistics:")
    stats = agent.get_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))