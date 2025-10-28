import sys, os, json, csv, threading
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5 import QtPrintSupport
from ai_agent import LocalAIAgent

LOG_DIR = os.path.join(os.getcwd(), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
JSON_LOG = os.path.join(LOG_DIR, 'workflows.json')
CSV_LOG = os.path.join(LOG_DIR, 'workflows.csv')

class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal(dict, str)
    error = QtCore.pyqtSignal(str, str)

    def __init__(self, agent: LocalAIAgent, text: str, model: str = None):
        super().__init__()
        self.agent = agent
        self.text = text
        self.model = model

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.agent.process_request(self.text, self.model)
            self.finished.emit(result, self.text)
        except Exception as e:
            self.error.emit(str(e), self.text)

class ChatWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JARVIS Desktop (PyQt5)')
        self.resize(1000, 700)
        self.agent = LocalAIAgent()
        self._init_ui()
        self._ensure_csv_header()
        self._load_history()
        self.current_transcript = []  # เก็บคู่สนทนาปัจจุบันในหน่วยความจำ

    def _init_ui(self):
        # Menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        action_export_txt = QtWidgets.QAction('Export Transcript (TXT)', self)
        action_export_txt.triggered.connect(self.export_transcript_txt)
        action_export_pdf = QtWidgets.QAction('Export Transcript (PDF)', self)
        action_export_pdf.triggered.connect(self.export_transcript_pdf)
        action_exit = QtWidgets.QAction('Exit', self)
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_export_txt)
        file_menu.addAction(action_export_pdf)
        file_menu.addSeparator()
        file_menu.addAction(action_exit)

        # Central splitter
        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Left: History/Conversations
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        self.list_history = QtWidgets.QListWidget()
        left_layout.addWidget(QtWidgets.QLabel('🗂️ ประวัติ (จากฐานข้อมูล)'))
        left_layout.addWidget(self.list_history)
        self.list_history.itemClicked.connect(self._on_history_clicked)
        splitter.addWidget(left)
        splitter.setStretchFactor(0, 1)

        # Right: Chat area
        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(QtWidgets.QLabel('🤖 Chat'))
        header.addStretch(1)
        self.model_combo = QtWidgets.QComboBox()
        models = [self.agent.default_model] + [m for m in self.agent.available_models if m != self.agent.default_model]
        self.model_combo.addItems(models)
        header.addWidget(QtWidgets.QLabel('Model:'))
        header.addWidget(self.model_combo)
        right_layout.addLayout(header)

        self.chat_view = QtWidgets.QTextBrowser()
        self.chat_view.setOpenExternalLinks(True)
        self.chat_view.setStyleSheet("QTextBrowser { background: #0f172a; color: #e2e8f0; border-radius: 8px; padding: 12px; }")
        right_layout.addWidget(self.chat_view)

        input_layout = QtWidgets.QHBoxLayout()
        self.input_edit = QtWidgets.QLineEdit()
        self.input_edit.setPlaceholderText('พิมพ์ข้อความของคุณ...')
        self.btn_send = QtWidgets.QPushButton('ส่ง')
        self.btn_send.clicked.connect(self.on_send)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(self.btn_send)
        right_layout.addLayout(input_layout)

        splitter.addWidget(right)
        splitter.setStretchFactor(1, 3)

        # Status bar
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)
        self._append_ai_message('สวัสดีครับ! ผม JARVIS พร้อมช่วยงานคุณ 🎯')

    def _append_user_message(self, text):
        ts = datetime.now().strftime('%H:%M')
        html = f"<div style='text-align:right; margin:8px 0;'><span style='background:#10b981; color:white; padding:8px 12px; border-radius:16px;'>{text}</span> <span style='color:#94a3b8; font-size:12px;'>{ts}</span></div>"
        self.chat_view.append(html)

    def _append_ai_message(self, text):
        ts = datetime.now().strftime('%H:%M')
        html = f"<div style='text-align:left; margin:8px 0;'><span style='background:#1f2937; color:#e5e7eb; padding:8px 12px; border-radius:16px; display:inline-block;'>{text}</span> <span style='color:#94a3b8; font-size:12px;'>{ts}</span></div>"
        self.chat_view.append(html)

    def on_send(self):
        text = self.input_edit.text().strip()
        if not text:
            return
        self._append_user_message(text)
        self.input_edit.clear()
        self.status.showMessage('กำลังประมวลผล...')
        self.btn_send.setEnabled(False)

        # Background worker
        self.thread = QtCore.QThread()
        self.worker = Worker(self.agent, text, self.model_combo.currentText())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_finished(self, result: dict, text: str):
        ai_text = result.get('ai_response', '')
        self._append_ai_message(ai_text)
        self.current_transcript.append(('user', text))
        self.current_transcript.append(('ai', ai_text))
        self._log_workflow(text, ai_text, result)
        self.status.showMessage(f"เสร็จสิ้นใน {result.get('processing_time','?')}s", 3000)
        self.btn_send.setEnabled(True)

    def on_error(self, err: str, text: str):
        self._append_ai_message(f"ขออภัย เกิดข้อผิดพลาด: {err}")
        self._log_workflow(text, f"ERROR: {err}", {})
        self.status.showMessage('เกิดข้อผิดพลาด', 3000)
        self.btn_send.setEnabled(True)

    def _ensure_csv_header(self):
        if not os.path.exists(CSV_LOG):
            with open(CSV_LOG, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp','user_input','ai_response','model','processing_time'])

    def _log_workflow(self, user_input: str, ai_response: str, result: dict):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'ai_response': ai_response,
            'model': result.get('model_used'),
            'processing_time': result.get('processing_time'),
            'internet_data': result.get('internet_data')
        }
        # JSON append
        try:
            existing = []
            if os.path.exists(JSON_LOG):
                with open(JSON_LOG, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            existing.append(entry)
            with open(JSON_LOG, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
        # CSV append
        try:
            with open(CSV_LOG, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([entry['timestamp'], user_input, ai_response, entry['model'], entry['processing_time']])
        except Exception:
            pass

    def _load_history(self):
        try:
            cur = self.agent.conn.cursor()
            cur.execute("SELECT id, timestamp, user_input, ai_response, model_used FROM agent_logs ORDER BY id DESC LIMIT 50")
            rows = cur.fetchall()
            self.list_history.clear()
            for rid, ts, ui, ai, model in rows:
                preview = ui[:30].replace('\n', ' ') + "..."
                item = QtWidgets.QListWidgetItem(f"[{ts.split('T')[0]}] {preview}")
                item.setData(QtCore.Qt.UserRole, (rid, ts, ui, ai, model))
                self.list_history.addItem(item)
        except Exception:
            pass

    def _on_history_clicked(self, item: QtWidgets.QListWidgetItem):
        data = item.data(QtCore.Qt.UserRole)
        if not data:
            return
        _, ts, ui, ai, model = data
        self.chat_view.clear()
        self._append_user_message(ui)
        self._append_ai_message(f"({model}) {ai}")

    def export_transcript_txt(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Transcript', 'transcript.txt', 'Text Files (*.txt)')
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                for role, text in self.current_transcript:
                    who = 'You' if role == 'user' else 'AI'
                    f.write(f"{who}: {text}\n\n")
            self.status.showMessage('บันทึกไฟล์ TXT สำเร็จ', 3000)
        except Exception as e:
            self.status.showMessage(f'บันทึกไม่สำเร็จ: {e}', 3000)

    def export_transcript_pdf(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Transcript', 'transcript.pdf', 'PDF Files (*.pdf)')
        if not path:
            return
        try:
            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            doc = QtGui.QTextDocument()
            html = "<h3>JARVIS Transcript</h3>"
            for role, text in self.current_transcript:
                who = 'You' if role == 'user' else 'AI'
                text_clean = text.replace('\n', '<br>')
                html += f"<p><b>{who}:</b> {text_clean}</p>"
            doc.setHtml(html)
            doc.print_(printer)
            self.status.showMessage('บันทึกไฟล์ PDF สำเร็จ', 3000)
        except Exception as e:
            self.status.showMessage(f'บันทึกไม่สำเร็จ: {e}', 3000)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = ChatWindow()
    win.show()
    sys.exit(app.exec_())
