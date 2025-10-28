import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from ai_agent import LocalAIAgent
import json
from datetime import datetime

class AIAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 JARVIS Local AI Agent - Phi-3 Enhanced")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")
        
        self.agent = LocalAIAgent()
        self.setup_ui()
        self.load_initial_stats()
    
    def setup_ui(self):
        """สร้างส่วนติดต่อผู้ใช้แบบครบครัน"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header Section
        self.setup_header(main_frame)
        
        # Control Panel
        self.setup_control_panel(main_frame)
        
        # Input/Output Section (ใช้ notebook tabs)
        self.setup_notebook_interface(main_frame)
        
        # Status Bar
        self.setup_status_bar(main_frame)
    
    def setup_header(self, parent):
        """ส่วนหัวของแอปพลิเคชัน"""
        header_frame = ttk.LabelFrame(parent, text="🧠 JARVIS AI System Status", padding=10)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Model info
        model_frame = ttk.Frame(header_frame)
        model_frame.pack(fill="x")
        
        ttk.Label(model_frame, text="Current Model:", font=("Arial", 10, "bold")).pack(side="left")
        self.model_label = ttk.Label(model_frame, text=self.agent.default_model, 
                                   foreground="green", font=("Arial", 10))
        self.model_label.pack(side="left", padx=(5, 0))
        
        # Ollama status
        self.status_label = ttk.Label(model_frame, text="🟢 Ollama Connected", 
                                    foreground="green", font=("Arial", 10))
        self.status_label.pack(side="right")
        
        # Stats summary
        stats_frame = ttk.Frame(header_frame)
        stats_frame.pack(fill="x", pady=(5, 0))
        
        self.stats_summary = ttk.Label(stats_frame, text="📊 Loading statistics...", 
                                     font=("Arial", 9))
        self.stats_summary.pack(side="left")
    
    def setup_control_panel(self, parent):
        """แผงควบคุม"""
        control_frame = ttk.LabelFrame(parent, text="⚙️ Control Panel", padding=10)
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Model selection
        ttk.Label(control_frame, text="Select Model:").pack(side="left")
        self.model_var = tk.StringVar(value=self.agent.default_model)
        self.model_combo = ttk.Combobox(control_frame, textvariable=self.model_var, 
                                      values=self.agent.available_models, width=20)
        self.model_combo.pack(side="left", padx=(5, 10))
        
        # Platform selection
        ttk.Label(control_frame, text="Platform:").pack(side="left")
        self.platform_var = tk.StringVar(value="auto")
        platform_combo = ttk.Combobox(control_frame, textvariable=self.platform_var,
                                     values=["auto", "reddit", "youtube", "facebook", "weather", "general"],
                                     width=10)
        platform_combo.pack(side="left", padx=(5, 10))
        
        # Control buttons
        ttk.Button(control_frame, text="🔄 Refresh Models", 
                  command=self.refresh_models).pack(side="right", padx=(5, 0))
        ttk.Button(control_frame, text="📊 Statistics", 
                  command=self.show_statistics).pack(side="right", padx=(5, 0))
        ttk.Button(control_frame, text="🗑️ Clear Logs", 
                  command=self.clear_display).pack(side="right", padx=(5, 0))
    
    def setup_notebook_interface(self, parent):
        """สร้าง notebook interface แบบ tabs"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Tab 1: Chat Interface
        self.setup_chat_tab()
        
        # Tab 2: Internet Data
        self.setup_internet_tab()
        
        # Tab 3: Logs & Analytics
        self.setup_logs_tab()
    
    def setup_chat_tab(self):
        """แท็บสำหรับการสนทนา"""
        chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(chat_frame, text="💬 Chat")
        
        # Input section
        input_frame = ttk.LabelFrame(chat_frame, text="Your Input", padding=10)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=4, font=("Arial", 11),
                                                  wrap=tk.WORD)
        self.input_text.pack(fill="x", pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="🚀 Send", command=self.process_input,
                  style="Accent.TButton").pack(side="left")
        ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_input).pack(side="left", padx=(5, 0))
        
        # Output section
        output_frame = ttk.LabelFrame(chat_frame, text="AI Response", padding=10)
        output_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.output_text = scrolledtext.ScrolledText(output_frame, font=("Arial", 10),
                                                   wrap=tk.WORD, state="disabled")
        self.output_text.pack(fill="both", expand=True)
        
    def setup_internet_tab(self):
        """แท็บสำหรับข้อมูลอินเทอร์เน็ต"""
        internet_frame = ttk.Frame(self.notebook)
        self.notebook.add(internet_frame, text="🌐 Internet Data")
        
        # Platform info
        platform_info_frame = ttk.LabelFrame(internet_frame, text="Platform Status", padding=10)
        platform_info_frame.pack(fill="x", padx=10, pady=10)
        
        self.platform_status = scrolledtext.ScrolledText(platform_info_frame, height=4,
                                                       font=("Courier", 9), state="disabled")
        self.platform_status.pack(fill="x")
        
        # Internet data display
        data_frame = ttk.LabelFrame(internet_frame, text="Latest Internet Data", padding=10)
        data_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.internet_data_display = scrolledtext.ScrolledText(data_frame, font=("Courier", 9),
                                                             wrap=tk.WORD, state="disabled")
        self.internet_data_display.pack(fill="both", expand=True)
        
    def setup_logs_tab(self):
        """แท็บสำหรับ logs และ analytics"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📊 Logs & Analytics")
        
        # Control buttons
        control_frame = ttk.Frame(logs_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(control_frame, text="📈 Refresh Stats", 
                  command=self.update_statistics).pack(side="left")
        ttk.Button(control_frame, text="💾 Export Logs", 
                  command=self.export_logs).pack(side="left", padx=(5, 0))
        ttk.Button(control_frame, text="🗃️ View Database", 
                  command=self.view_database).pack(side="left", padx=(5, 0))
        
        # Statistics display
        stats_frame = ttk.LabelFrame(logs_frame, text="Performance Statistics", padding=10)
        stats_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.stats_display = scrolledtext.ScrolledText(stats_frame, font=("Courier", 9),
                                                     wrap=tk.WORD, state="disabled")
        self.stats_display.pack(fill="both", expand=True)
    
    def setup_status_bar(self, parent):
        """แถบสถานะ"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x")
        
        self.status_text = ttk.Label(status_frame, text="Ready", relief="sunken", anchor="w")
        self.status_text.pack(side="left", fill="x", expand=True)
        
        self.processing_indicator = ttk.Label(status_frame, text="💤 Idle", relief="sunken")
        self.processing_indicator.pack(side="right")
    
    def load_initial_stats(self):
        """โหลดสถิติเริ่มต้น"""
        try:
            stats = self.agent.get_statistics()
            total_requests = stats['overall']['total_requests']
            success_rate = stats['overall']['success_rate']
            self.stats_summary.config(text=f"📊 Total Requests: {total_requests} | Success Rate: {success_rate}%")
            
            # อัปเดต platform status
            self.update_platform_status()
        except Exception as e:
            self.stats_summary.config(text=f"📊 Stats loading error: {str(e)}")
    
    def update_platform_status(self):
        """อัปเดตสถานะ platform"""
        status_text = "🌐 Platform Status:\n"
        status_text += f"✅ Reddit API: Available (No auth required)\n"
        status_text += f"⚠️ YouTube API: Requires API key\n"
        status_text += f"⚠️ Facebook API: Requires access token\n"
        status_text += f"✅ Weather API: Available (wttr.in)\n"
        status_text += f"✅ General APIs: Available\n"
        
        self.platform_status.config(state="normal")
        self.platform_status.delete(1.0, tk.END)
        self.platform_status.insert(tk.END, status_text)
        self.platform_status.config(state="disabled")
    
    def process_input(self):
        """ประมวลผลคำสั่งจากผู้ใช้"""
        user_input = self.input_text.get(1.0, tk.END).strip()
        if not user_input:
            messagebox.showwarning("Warning", "Please enter a command!")
            return
        
        # แสดงสถานะกำลังประมวลผล
        self.processing_indicator.config(text="🔄 Processing...")
        self.status_text.config(text="Processing your request...")
        
        # ใช้ thread เพื่อไม่ให้ GUI หยุดทำงาน
        thread = threading.Thread(target=self._process_in_background, args=(user_input,))
        thread.daemon = True
        thread.start()
    
    def _process_in_background(self, user_input):
        """ประมวลผลในพื้นหลัง"""
        try:
            # กำหนด model และ platform
            selected_model = self.model_var.get() if self.model_var.get() != self.agent.default_model else None
            
            # ถ้าเลือก platform manual ให้ override
            if self.platform_var.get() != "auto":
                # แก้ไข user input เพื่อบังคับ platform
                platform_keywords = {
                    "reddit": "reddit",
                    "youtube": "youtube", 
                    "facebook": "facebook",
                    "weather": "สภาพอากาศ",
                    "general": "ค้นหา"
                }
                if self.platform_var.get() in platform_keywords:
                    user_input = f"{platform_keywords[self.platform_var.get()]} {user_input}"
            
            # เรียก agent
            result = self.agent.process_request(user_input, selected_model)
            
            # อัปเดต GUI ใน main thread
            self.root.after(0, self._update_results, user_input, result)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _update_results(self, user_input, result):
        """อัปเดตผลลัพธ์ใน GUI"""
        # แสดงใน chat tab
        self.output_text.config(state="normal")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"\n[{timestamp}] You: {user_input}\n")
        self.output_text.insert(tk.END, f"[{timestamp}] AI ({result['model_used']}): {result['ai_response']}\n")
        
        if result.get('internet_data'):
            self.output_text.insert(tk.END, f"[{timestamp}] 🌐 Platform: {result['platform_detected']}\n")
        
        self.output_text.insert(tk.END, f"⏱️ Processing time: {result['processing_time']}s\n")
        self.output_text.insert(tk.END, "-" * 50 + "\n")
        
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")
        
        # แสดง internet data ใน internet tab
        if result.get('internet_data'):
            self.internet_data_display.config(state="normal")
            self.internet_data_display.delete(1.0, tk.END)
            formatted_data = json.dumps(result['internet_data'], indent=2, ensure_ascii=False)
            self.internet_data_display.insert(tk.END, formatted_data)
            self.internet_data_display.config(state="disabled")
        
        # อัปเดตสถานะ
        self.processing_indicator.config(text="✅ Complete")
        self.status_text.config(text=f"Request completed in {result['processing_time']}s")
        
        # อัปเดตสถิติ
        self.update_statistics()
        
        # ล้าง input
        self.input_text.delete(1.0, tk.END)
    
    def _show_error(self, error_msg):
        """แสดงข้อผิดพลาด"""
        self.processing_indicator.config(text="❌ Error")
        self.status_text.config(text=f"Error: {error_msg}")
        messagebox.showerror("Error", f"An error occurred: {error_msg}")
    
    def clear_input(self):
        """ล้าง input text"""
        self.input_text.delete(1.0, tk.END)
    
    def clear_display(self):
        """ล้างการแสดงผล"""
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")
        
        self.internet_data_display.config(state="normal")
        self.internet_data_display.delete(1.0, tk.END)
        self.internet_data_display.config(state="disabled")
    
    def refresh_models(self):
        """รีเฟรชรายชื่อโมเดล"""
        self.agent.load_available_models()
        self.model_combo['values'] = self.agent.available_models
        self.model_label.config(text=self.agent.default_model)
        messagebox.showinfo("Success", f"Models refreshed! Found {len(self.agent.available_models)} models.")
    
    def update_statistics(self):
        """อัปเดตสถิติ"""
        try:
            stats = self.agent.get_statistics()
            
            # อัปเดต summary
            total_requests = stats['overall']['total_requests']
            success_rate = stats['overall']['success_rate']
            avg_time = stats['overall']['avg_response_time']
            self.stats_summary.config(text=f"📊 Requests: {total_requests} | Success: {success_rate}% | Avg Time: {avg_time}s")
            
            # แสดงใน logs tab
            stats_text = "📊 PERFORMANCE STATISTICS\n"
            stats_text += "=" * 50 + "\n\n"
            
            stats_text += f"Overall Performance:\n"
            stats_text += f"  Total Requests: {total_requests}\n"
            stats_text += f"  Success Rate: {success_rate}%\n"
            stats_text += f"  Average Response Time: {avg_time}s\n\n"
            
            stats_text += "By Model:\n"
            for model_stat in stats['by_model']:
                stats_text += f"  {model_stat['model']}: {model_stat['requests']} requests, "
                stats_text += f"{model_stat['success_rate']}% success, {model_stat['avg_time']}s avg\n"
            
            stats_text += "\nInternet Usage:\n"
            for internet_stat in stats['internet_usage']:
                stats_text += f"  {internet_stat['platform']}: {internet_stat['requests']} requests, "
                stats_text += f"{internet_stat['success_rate']}% success\n"
            
            self.stats_display.config(state="normal")
            self.stats_display.delete(1.0, tk.END)
            self.stats_display.insert(tk.END, stats_text)
            self.stats_display.config(state="disabled")
            
        except Exception as e:
            self.stats_summary.config(text=f"📊 Stats error: {str(e)}")
    
    def show_statistics(self):
        """แสดงหน้าต่างสถิติแยกต่างหาก"""
        self.notebook.select(2)  # เปลี่ยนไปแท็บ logs
        self.update_statistics()
    
    def export_logs(self):
        """ส่งออก logs เป็นไฟล์"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jarvis_logs_{timestamp}.json"
            
            stats = self.agent.get_statistics()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", f"Logs exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def view_database(self):
        """ดูข้อมูลในฐานข้อมูล (แสดงแบบง่าย ๆ)"""
        try:
            cursor = self.agent.conn.cursor()
            cursor.execute("SELECT timestamp, user_input, model_used, success FROM agent_logs ORDER BY id DESC LIMIT 10")
            recent_logs = cursor.fetchall()
            
            log_text = "📚 RECENT DATABASE ENTRIES (Last 10)\n"
            log_text += "=" * 60 + "\n\n"
            
            for log in recent_logs:
                timestamp, user_input, model, success = log
                status = "✅" if success else "❌"
                log_text += f"{status} [{timestamp}] Model: {model}\n"
                log_text += f"    Input: {user_input[:50]}...\n\n"
            
            # แสดงในหน้าต่างใหม่
            db_window = tk.Toplevel(self.root)
            db_window.title("Database Viewer")
            db_window.geometry("600x400")
            
            db_text = scrolledtext.ScrolledText(db_window, font=("Courier", 9))
            db_text.pack(fill="both", expand=True, padx=10, pady=10)
            db_text.insert(tk.END, log_text)
            db_text.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error", f"Database view failed: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AIAgentGUI(root)
    root.mainloop()