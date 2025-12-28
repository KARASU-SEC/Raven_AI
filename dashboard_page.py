"""
Страница дашборда с метриками системы и быстрыми действиями
"""
import os
import psutil
import webbrowser
import platform
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout,
                             QListWidget, QListWidgetItem, QLineEdit, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont

from ui.components.metric_card import MetricCard
from ui.components.chat_message import ChatMessage

class DashboardPage(QWidget):
    """Страница дашборда"""
    
    def __init__(self, raven_ai):
        super().__init__()
        self.raven = raven_ai
        self.chat_history = []
        
        self.setup_ui()
        self.setup_timers()
        
        # Приветственное сообщение
        self.add_chat_message("Hello! I'm Raven AI, your personal assistant. How can I help you today?", False)
    
    def setup_ui(self):
        """Настройка интерфейса страницы"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Первый ряд: метрики системы
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(20)
        
        self.cpu_card = MetricCard("CPU Usage", "0%", "💻", "+2.5%", "#3498db")
        self.ram_card = MetricCard("Memory", "0%", "🧠", "-1.2%", "#2ecc71")
        self.disk_card = MetricCard("Disk", "0%", "💾", "+0.8%", "#9b59b6")
        self.process_card = MetricCard("Processes", "0", "⚙️", "+3", "#e74c3c")
        
        metrics_layout.addWidget(self.cpu_card)
        metrics_layout.addWidget(self.ram_card)
        metrics_layout.addWidget(self.disk_card)
        metrics_layout.addWidget(self.process_card)
        layout.addLayout(metrics_layout)
        
        # Второй ряд: чат и действия
        second_row = QHBoxLayout()
        second_row.setSpacing(20)
        
        # Чат с ассистентом
        chat_card = QFrame()
        chat_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        chat_card.setMinimumHeight(400)
        
        chat_layout = QVBoxLayout(chat_card)
        chat_layout.setContentsMargins(20, 20, 20, 20)
        chat_layout.setSpacing(15)
        
        # Заголовок чата
        chat_header = QHBoxLayout()
        chat_title = QLabel("🤖 AI Assistant Chat")
        chat_title.setStyleSheet("""
            color: #2c3e50;
            font-size: 18px;
            font-weight: 700;
        """)
        chat_header.addWidget(chat_title)
        
        voice_btn = QPushButton("🎤 Voice Input")
        voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        voice_btn.clicked.connect(self.start_voice_input)
        chat_header.addWidget(voice_btn)
        chat_header.addStretch()
        chat_layout.addLayout(chat_header)
        
        # Прокручиваемая область чата
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(5, 5, 5, 5)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_widget)
        chat_layout.addWidget(self.chat_scroll)
        
        # Поле ввода
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message or command...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.chat_input.returnPressed.connect(self.send_chat_message)
        
        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        send_btn.clicked.connect(self.send_chat_message)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)
        chat_layout.addLayout(input_layout)
        
        # Быстрые действия
        actions_card = QFrame()
        actions_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        actions_card.setMinimumHeight(400)
        actions_card.setFixedWidth(350)
        
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(20, 20, 20, 20)
        actions_layout.setSpacing(15)
        
        actions_title = QLabel("⚡ Quick Actions")
        actions_title.setStyleSheet("""
            color: #2c3e50;
            font-size: 18px;
            font-weight: 700;
        """)
        actions_layout.addWidget(actions_title)
        
        # Кнопки быстрых действий
        quick_actions = [
            ("🌐 Open Browser", self.open_browser),
            ("📊 System Info", self.show_system_info),
            ("🧹 Clean RAM", self.clean_ram),
            ("🎤 Voice Command", self.start_voice_input),
            ("📷 Screenshot", self.take_screenshot),
            ("⚙️ Settings", lambda: self.show_notification("Opening settings..."))
        ]
        
        for text, callback in quick_actions:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #3498db;
                }
            """)
            btn.clicked.connect(callback)
            actions_layout.addWidget(btn)
        
        actions_layout.addStretch()
        
        second_row.addWidget(chat_card, stretch=2)
        second_row.addWidget(actions_card)
        layout.addLayout(second_row)
        
        # Третий ряд: процессы
        processes_card = QFrame()
        processes_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        processes_card.setMinimumHeight(250)
        
        processes_layout = QVBoxLayout(processes_card)
        processes_layout.setContentsMargins(20, 20, 20, 20)
        
        processes_header = QHBoxLayout()
        processes_title = QLabel("📊 Top Processes")
        processes_title.setStyleSheet("""
            color: #2c3e50;
            font-size: 18px;
            font-weight: 700;
        """)
        processes_header.addWidget(processes_title)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        refresh_btn.clicked.connect(self.update_processes_list)
        processes_header.addWidget(refresh_btn)
        processes_header.addStretch()
        processes_layout.addLayout(processes_header)
        
        self.processes_list = QListWidget()
        self.processes_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        processes_layout.addWidget(self.processes_list)
        
        layout.addWidget(processes_card)
        
        layout.addStretch()
    
    def setup_timers(self):
        """Настройка таймеров"""
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.update_metrics)
        self.metrics_timer.start(3000)
        
        self.update_metrics()
        self.update_processes_list()
    
    def update_metrics(self):
        """Обновление метрик системы"""
        try:
            cpu_percent = psutil.cpu_percent()
            self.cpu_card.set_value(f"{cpu_percent:.1f}%")
            
            ram = psutil.virtual_memory()
            self.ram_card.set_value(f"{ram.percent:.1f}%")
            
            disk = psutil.disk_usage('C:/' if os.name == 'nt' else '/')
            self.disk_card.set_value(f"{disk.percent:.1f}%")
            
            processes = len(psutil.pids())
            self.process_card.set_value(str(processes))
            
        except Exception as e:
            print(f"Metrics update error: {e}")
    
    def update_processes_list(self):
        """Обновление списка процессов"""
        self.processes_list.clear()
        try:
            for proc in sorted(psutil.process_iter(['name', 'cpu_percent']), 
                             key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:10]:
                info = proc.info
                name = info['name'][:30]
                cpu = info['cpu_percent'] or 0
                
                item = QListWidgetItem(f"{name} - CPU: {cpu:.1f}%")
                self.processes_list.addItem(item)
        except Exception as e:
            print(f"Process list error: {e}")
    
    def add_chat_message(self, text, is_user=False):
        """Добавление сообщения в чат"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        message_widget = ChatMessage(text, is_user, timestamp)
        
        # Сохраняем в историю
        self.chat_history.append({
            'text': text,
            'is_user': is_user,
            'time': timestamp
        })
        
        # Удаляем stretch, добавляем сообщение, снова stretch
        self.chat_layout.removeItem(self.chat_layout.itemAt(self.chat_layout.count() - 1))
        self.chat_layout.addWidget(message_widget)
        self.chat_layout.addStretch()
        
        # Прокрутка вниз
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
    
    def send_chat_message(self):
        """Отправка текстового сообщения"""
        text = self.chat_input.text().strip()
        if not text:
            return
        
        self.add_chat_message(text, True)
        self.chat_input.clear()
        
        # Обработка через ИИ
        response = self.raven.process_command(text)
        self.add_chat_message(response, False)
    
    def start_voice_input(self):
        """Запуск голосового ввода"""
        if not self.raven.is_voice_active:
            self.add_chat_message("Voice is disabled. Enable it in settings.", False)
            return
        
        self.add_chat_message("🎤 Listening...", True)
        
        # Импортируем threading локально
        import threading
        
        def listen_thread():
            text = self.raven.listen(timeout=10)
            if text:
                self.add_chat_message(text, True)
                response = self.raven.process_command(text)
                self.add_chat_message(response, False)
            else:
                self.add_chat_message("❌ Could not recognize speech", False)
        
        thread = threading.Thread(target=listen_thread, daemon=True)
        thread.start()
    
    def open_browser(self):
        """Открыть браузер"""
        webbrowser.open("https://www.google.com")
        self.add_chat_message("Opening browser...", False)
    
    def show_system_info(self):
        """Показать информацию о системе"""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('C:/' if os.name == 'nt' else '/').percent
        
        info = f"""System Information:
• CPU: {cpu}%
• RAM: {ram}%
• Disk: {disk}%
• OS: {platform.system()} {platform.release()}
• Python: {platform.python_version()}"""
        
        self.add_chat_message(info, False)
        self.raven.speak(f"CPU {cpu} percent, RAM {ram} percent, Disk {disk} percent")
    
    def clean_ram(self):
        """Очистка RAM"""
        import gc
        gc.collect()
        self.add_chat_message("RAM cleaned up", False)
        self.raven.speak("RAM cleaned")
    
    def take_screenshot(self):
        """Сделать скриншот"""
        try:
            from PIL import ImageGrab
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            ImageGrab.grab().save(filename)
            self.add_chat_message(f"Screenshot saved as {filename}", False)
        except ImportError:
            self.add_chat_message("Install Pillow for screenshots: pip install pillow", False)
    
    def show_notification(self, message):
        """Показать уведомление"""
        self.add_chat_message(message, False)
    
    def cleanup(self):
        """Очистка ресурсов при закрытии"""
        if hasattr(self, 'metrics_timer'):
            self.metrics_timer.stop()