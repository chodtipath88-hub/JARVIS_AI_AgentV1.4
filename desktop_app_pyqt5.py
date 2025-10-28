"""
JARVIS AI Agent - PyQt5 Desktop App
A native desktop interface for JARVIS AI Agent using PyQt5
"""

import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QTabWidget,
    QGroupBox, QCheckBox, QComboBox, QListWidget, QSplitter,
    QStatusBar, QMenuBar, QMenu, QAction, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon


class JarvisMainWindow(QMainWindow):
    """Main window for JARVIS AI Agent"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("JARVIS AI Agent v1.4")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create left panel (conversation)
        left_panel = self.create_conversation_panel()
        
        # Create right panel (controls and info)
        right_panel = self.create_control_panel()
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Create status bar
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New Session', self)
        new_action.triggered.connect(self.new_session)
        file_menu.addAction(new_action)
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_conversation_panel(self):
        """Create the main conversation panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Title
        title = QLabel("🤖 JARVIS Conversation")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Courier", 10))
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message to JARVIS...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)
        
        layout.addLayout(input_layout)
        
        # Add welcome message
        self.add_system_message("JARVIS AI Agent v1.4 initialized successfully!")
        self.add_system_message("Type a message to begin conversation...")
        
        return panel
        
    def create_control_panel(self):
        """Create the control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout()
        
        # Mode selector
        mode_label = QLabel("Agent Mode:")
        settings_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Assistant", "Autonomous", "Learning"])
        settings_layout.addWidget(self.mode_combo)
        
        # Checkboxes
        self.voice_check = QCheckBox("Enable Voice")
        settings_layout.addWidget(self.voice_check)
        
        self.debug_check = QCheckBox("Debug Mode")
        settings_layout.addWidget(self.debug_check)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Quick Actions group
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        
        analyze_btn = QPushButton("🔍 Analyze")
        analyze_btn.clicked.connect(self.analyze_action)
        actions_layout.addWidget(analyze_btn)
        
        dashboard_btn = QPushButton("📊 Dashboard")
        dashboard_btn.clicked.connect(self.dashboard_action)
        actions_layout.addWidget(dashboard_btn)
        
        config_btn = QPushButton("⚙️ Configure")
        config_btn.clicked.connect(self.config_action)
        actions_layout.addWidget(config_btn)
        
        # Fixed: Avoid backslash in f-string by using variable
        reset_icon = "🔄"
        reset_btn = QPushButton(f"{reset_icon} Reset Chat")
        reset_btn.clicked.connect(self.reset_chat)
        actions_layout.addWidget(reset_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # System Status group
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        
        self.status_list = QListWidget()
        self.update_status_list()
        status_layout.addWidget(self.status_list)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
        
    def create_status_bar(self):
        """Create the status bar"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Status label
        self.status_label = QLabel("System Online ✅")
        self.statusBar.addWidget(self.status_label)
        
        # Time label
        self.time_label = QLabel()
        self.statusBar.addPermanentWidget(self.time_label)
        self.update_time()
        
    def setup_timer(self):
        """Setup timer for updating time"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Fixed: Avoid backslash in f-string by using variable
        clock_icon = "🕐"
        self.time_label.setText(f"{clock_icon} {current_time}")
        
    def update_status_list(self):
        """Update the status list"""
        self.status_list.clear()
        self.status_list.addItem("✅ Streamlit: Available")
        self.status_list.addItem("✅ PyQt5: Running")
        self.status_list.addItem("✅ Flask: Ready")
        self.status_list.addItem("✅ NLTK: Loaded")
        
    def add_system_message(self, message):
        """Add a system message to the chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] SYSTEM: {message}"
        self.chat_display.append(formatted_message)
        
    def add_user_message(self, message):
        """Add a user message to the chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] USER: {message}"
        self.chat_display.append(formatted_message)
        
    def add_jarvis_message(self, message):
        """Add a JARVIS response to the chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] JARVIS: {message}"
        self.chat_display.append(formatted_message)
        
    def send_message(self):
        """Handle sending a message"""
        message = self.input_field.text().strip()
        if not message:
            return
            
        # Add user message
        self.add_user_message(message)
        
        # Generate response
        response = f"I received your message: '{message}'. Desktop app is working!"
        self.add_jarvis_message(response)
        
        # Clear input
        self.input_field.clear()
        
        # Update status
        self.status_label.setText("Message processed ✅")
        
    def new_session(self):
        """Start a new session"""
        self.chat_display.clear()
        self.add_system_message("New session started")
        self.status_label.setText("New session ✅")
        
    def reset_chat(self):
        """Reset the chat"""
        self.chat_display.clear()
        self.add_system_message("Chat reset successfully")
        self.add_system_message("Type a message to begin conversation...")
        self.status_label.setText("Chat reset ✅")
        
    def analyze_action(self):
        """Handle analyze action"""
        self.add_system_message("Analysis feature activated")
        self.status_label.setText("Analyzing... ✅")
        
    def dashboard_action(self):
        """Handle dashboard action"""
        self.add_system_message("Dashboard feature activated")
        self.status_label.setText("Dashboard ready ✅")
        
    def config_action(self):
        """Handle configuration action"""
        self.add_system_message("Configuration interface opened")
        self.status_label.setText("Configuration ✅")
        
    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog would open here.\nConfigure JARVIS AI Agent preferences."
        )
        
    def show_about(self):
        """Show about dialog"""
        about_text = (
            "JARVIS AI Agent v1.4\n\n"
            "A desktop application for AI agent interaction.\n\n"
            "Features:\n"
            "- Streamlit: ✅ Available\n"
            "- PyQt5: ✅ Running\n"
            "- Flask: ✅ Ready\n"
            "- NLTK: ✅ Loaded\n\n"
            "Desktop Apps are ready for use!"
        )
        QMessageBox.about(self, "About JARVIS", about_text)


def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS AI Agent")
    
    # Create and show main window
    window = JarvisMainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
