"""
Современный дашборд Raven AI в стиле аналитической панели
"""
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QStackedWidget,
                             QTextEdit, QLineEdit, QGridLayout, QScrollArea,
                             QSizePolicy, QListWidget, QListWidgetItem,
                             QProgressBar, QSlider, QComboBox, QCheckBox)
from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve,
                         QParallelAnimationGroup, pyqtProperty, QSize, QPoint)
from PyQt6.QtGui import (QFont, QColor, QPalette, QLinearGradient, QPainter,
                        QPainterPath, QBrush, QPen, QPixmap, QIcon, QFontDatabase)
import psutil
import time
from datetime import datetime
import threading
import json
import math

class RoundedCard(QFrame):
    """Карточка с закруглёнными углами в стиле дашборда"""
    def __init__(self, parent=None, radius=12, bg_color="#ffffff"):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: {radius}px;
                border: 1px solid #e0e0e0;
            }}
        """)
        self.setMinimumHeight(100)

class MetricCard(RoundedCard):
    """Карточка с метрикой"""
    def __init__(self, title, value, icon="", trend="", parent=None):
        super().__init__(parent, bg_color="#ffffff")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок и иконка
        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #666666;
            font-size: 14px;
            font-weight: 500;
        """)
        header.addWidget(title_label)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 16px;")
            header.addWidget(icon_label)
            header.setAlignment(icon_label, Qt.AlignmentFlag.AlignRight)
        
        header.addStretch()
        layout.addLayout(header)
        
        # Значение
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            color: #2c3e50;
            font-size: 32px;
            font-weight: 700;
            margin: 10px 0;
        """)
        layout.addWidget(self.value_label)
        
        # Тренд (если есть)
        if trend:
            trend_layout = QHBoxLayout()
            trend_label = QLabel(trend)
            color = "#2ecc71" if trend.startswith("+") else "#e74c3c"
            trend_label.setStyleSheet(f"""
                color: {color};
                font-size: 12px;
                font-weight: 600;
                padding: 4px 8px;
                background-color: {color}15;
                border-radius: 4px;
            """)
            trend_layout.addWidget(trend_label)
            trend_layout.addStretch()
            layout.addLayout(trend_layout)

class ChatMessage(QFrame):
    """Сообщение в чате"""
    def __init__(self, text, is_user=False, time="", parent=None):
        super().__init__(parent)
        self.is_user = is_user
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Текст сообщения
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(f"""
            QLabel {{
                color: {'#2c3e50' if is_user else '#ffffff'};
                font-size: 14px;
                line-height: 1.4;
                padding: 12px 16px;
                background-color: {'#f8f9fa' if is_user else '#3498db'};
                border-radius: 18px;
                border: {'1px solid #e0e0e0' if is_user else 'none'};
            }}
        """)
        text_label.setMaximumWidth(400)
        text_label.setTextFormat(Qt.TextFormat.RichText)
        
        # Время
        time_label = QLabel(time)
        time_label.setStyleSheet("""
            color: #95a5a6;
            font-size: 11px;
            margin-top: 4px;
        """)
        
        layout.addWidget(text_label)
        layout.addWidget(time_label)
        
        # Выравнивание для пользователя
        if is_user:
            layout.setAlignment(Qt.AlignmentFlag.AlignRight)

# ИСПРАВЛЕНО: Убираем циклическую зависимость - это отдельное окно, а не класс из dashboard_main.py
class DashboardUIWindow(QMainWindow):
    """Главное окно дашборда (отдельная реализация)"""
    
    def __init__(self, raven_ai):
        super().__init__()
        self.raven = raven_ai
        self.setWindowTitle("Raven AI Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)
        
        # Загрузка конфига
        self.config = self.load_config()
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Боковая панель
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Основная область
        main_content = QWidget()
        main_content_layout = QVBoxLayout(main_content)
        main_content_layout.setSpacing(0)
        main_content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Верхняя панель
        self.topbar = self.create_topbar()
        main_content_layout.addWidget(self.topbar)
        
        # Контент с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                border-radius: 4px;
                min-height: 20px;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.setup_dashboard()
        
        scroll_area.setWidget(self.content_widget)
        main_content_layout.addWidget(scroll_area)
        
        main_layout.addWidget(main_content, stretch=1)
        
        # Таймеры
        self.setup_timers()
        
        # Инициализация данных
        self.update_dashboard()
        
        # Загружаем историю чата
        self.load_chat_history()
    
    def load_config(self):
        """Загрузка конфигурации"""
        config_path = os.path.join('config', 'dashboard_config.json')
        default_config = {
            "theme": "light",
            "accent_color": "#3498db",
            "sidebar_width": 280
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        return default_config
    
    def create_sidebar(self):
        """Создание боковой панели"""
        sidebar = QFrame()
        sidebar.setFixedWidth(self.config.get('sidebar_width', 280))
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Логотип
        logo_frame = QFrame()
        logo_frame.setFixedHeight(80)
        logo_frame.setStyleSheet("""
            QFrame {
                background-color: #1a252f;
                border-bottom: 1px solid #34495e;
            }
        """)
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 0, 20, 0)
        
        logo = QLabel("🤖 RAVEN AI")
        logo.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20px;
                font-weight: 700;
            }
        """)
        logo_layout.addWidget(logo)
        sidebar_layout.addWidget(logo_frame)
        
        # Навигация
        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("🎤", "Voice Control", "voice"),
            ("⚙️", "System Monitor", "system"),
            ("📈", "Analytics", "analytics"),
            ("🤖", "AI Assistant", "ai"),
            ("⚡", "Quick Actions", "actions"),
            ("🔧", "Settings", "settings"),
            ("❓", "Help", "help")
        ]
        
        self.nav_buttons = []
        for icon, text, id in nav_items:
            btn = QPushButton(f"  {icon}  {text}")
            btn.setObjectName(id)
            btn.setFixedHeight(50)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #bdc3c7;
                    border: none;
                    text-align: left;
                    padding-left: 25px;
                    font-size: 14px;
                    font-weight: 500;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                    color: #ecf0f1;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    color: white;
                    border-left: 4px solid #2980b9;
                }
            """)
            btn.clicked.connect(self.on_nav_clicked)
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        # Выделяем первый элемент
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
        
        sidebar_layout.addStretch()
        
        # Профиль пользователя
        profile_frame = QFrame()
        profile_frame.setFixedHeight(80)
        profile_frame.setStyleSheet("""
            QFrame {
                background-color: #1a252f;
                border-top: 1px solid #34495e;
            }
        """)
        profile_layout = QHBoxLayout(profile_frame)
        profile_layout.setContentsMargins(15, 10, 15, 10)
        
        avatar = QLabel("👤")
        avatar.setStyleSheet("""
            QLabel {
                font-size: 24px;
                padding: 8px;
                background-color: #3498db;
                border-radius: 20px;
                color: white;
            }
        """)
        avatar.setFixedSize(40, 40)
        
        user_info = QVBoxLayout()
        user_name = QLabel("User")
        user_name.setStyleSheet("""
            color: #ecf0f1;
            font-weight: 600;
            font-size: 14px;
        """)
        user_role = QLabel("Admin")
        user_role.setStyleSheet("""
            color: #95a5a6;
            font-size: 12px;
        """)
        user_info.addWidget(user_name)
        user_info.addWidget(user_role)
        
        profile_layout.addWidget(avatar)
        profile_layout.addLayout(user_info)
        sidebar_layout.addWidget(profile_frame)
        
        return sidebar
    
    def create_topbar(self):
        """Создание верхней панели"""
        topbar = QFrame()
        topbar.setFixedHeight(70)
        topbar.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(25, 0, 25, 0)
        
        # Заголовок страницы
        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 22px;
                font-weight: 700;
            }
        """)
        topbar_layout.addWidget(self.page_title)
        
        topbar_layout.addStretch()
        
        # Поиск
        search_frame = QFrame()
        search_frame.setFixedWidth(300)
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        search_icon = QLabel("🔍")
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search commands, settings...")
        search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                font-size: 14px;
                color: #2c3e50;
            }
        """)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(search_input)
        topbar_layout.addWidget(search_frame)
        
        # Уведомления
        notification_btn = QPushButton("🔔")
        notification_btn.setFixedSize(40, 40)
        notification_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 8px;
                font-size: 16px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Статус ассистента
        self.status_indicator = QPushButton()
        self.status_indicator.setFixedSize(40, 40)
        self.status_indicator.setCheckable(True)
        self.status_indicator.setChecked(True)
        self.update_status_indicator()
        self.status_indicator.clicked.connect(self.toggle_assistant_status)
        
        topbar_layout.addWidget(notification_btn)
        topbar_layout.addWidget(self.status_indicator)
        
        return topbar
    
    def setup_dashboard(self):
        """Настройка содержимого дашборда"""
        
        # Первый ряд: Ключевые метрики
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(20)
        
        self.cpu_card = MetricCard("CPU Usage", "0%", "💻", "+2.5%")
        self.ram_card = MetricCard("Memory", "0%", "🧠", "-1.2%")
        self.disk_card = MetricCard("Disk", "0%", "💾", "+0.8%")
        self.process_card = MetricCard("Processes", "0", "⚙️", "+3")
        
        metrics_row.addWidget(self.cpu_card)
        metrics_row.addWidget(self.ram_card)
        metrics_row.addWidget(self.disk_card)
        metrics_row.addWidget(self.process_card)
        self.content_layout.addLayout(metrics_row)
        
        # Второй ряд: График и чат
        second_row = QHBoxLayout()
        second_row.setSpacing(20)
        
        # График нагрузки (упрощённый)
        graph_card = RoundedCard()
        graph_card.setMinimumHeight(300)
        graph_layout = QVBoxLayout(graph_card)
        
        graph_header = QHBoxLayout()
        graph_title = QLabel("System Load")
        graph_title.setStyleSheet("""
            color: #2c3e50;
            font-size: 16px;
            font-weight: 600;
        """)
        graph_header.addWidget(graph_title)
        
        time_filter = QComboBox()
        time_filter.addItems(["Last hour", "Today", "Week", "Month"])
        time_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 5px 10px;
                min-width: 100px;
            }
        """)
        graph_header.addWidget(time_filter)
        graph_header.addStretch()
        
        graph_layout.addLayout(graph_header)
        
        # Простой график (заглушка)
        graph_widget = QLabel("📈 Real-time system load graph")
        graph_widget.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 14px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        graph_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        graph_layout.addWidget(graph_widget)
        
        # Чат с ассистентом
        chat_card = RoundedCard()
        chat_card.setMinimumHeight(300)
        chat_layout = QVBoxLayout(chat_card)
        
        chat_header = QHBoxLayout()
        chat_title = QLabel("AI Assistant Chat")
        chat_title.setStyleSheet("""
            color: #2c3e50;
            font-size: 16px;
            font-weight: 600;
        """)
        chat_header.addWidget(chat_title)
        
        voice_btn = QPushButton("🎤 Voice Input")
        voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        voice_btn.clicked.connect(self.start_voice_input)
        chat_header.addWidget(voice_btn)
        chat_header.addStretch()
        
        chat_layout.addLayout(chat_header)
        
        # Область чата
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_widget)
        chat_layout.addWidget(self.chat_scroll)
        
        # Поле ввода
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
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
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        send_btn.clicked.connect(self.send_chat_message)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)
        chat_layout.addLayout(input_layout)
        
        second_row.addWidget(graph_card, stretch=2)
        second_row.addWidget(chat_card, stretch=3)
        self.content_layout.addLayout(second_row)
        
        # Третий ряд: Процессы и быстрые действия
        third_row = QHBoxLayout()
        third_row.setSpacing(20)
        
        # Активные процессы
        processes_card = RoundedCard()
        processes_layout = QVBoxLayout(processes_card)
        
        processes_header = QHBoxLayout()
        processes_title = QLabel("Top Processes")
        processes_title.setStyleSheet("""
            color: #2c3e50;
            font-size: 16px;
            font-weight: 600;
        """)
        processes_header.addWidget(processes_title)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """)
        refresh_btn.clicked.connect(self.update_processes)
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
        
        # Быстрые действия
        actions_card = RoundedCard()
        actions_layout = QVBoxLayout(actions_card)
        
        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet("""
            color: #2c3e50;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
        """)
        actions_layout.addWidget(actions_title)
        
        # Кнопки быстрых действий
        actions_grid = QGridLayout()
        actions = [
            ("Open Browser", "🌐", self.open_browser),
            ("System Info", "📊", self.show_system_info),
            ("Clean RAM", "🧹", self.clean_ram),
            ("Voice Command", "🎤", self.start_voice_command),
            ("Take Screenshot", "📷", self.take_screenshot),
            ("Open Settings", "⚙️", self.open_settings)
        ]
        
        for i, (text, icon, callback) in enumerate(actions):
            btn = QPushButton(f"{icon} {text}")
            btn.setMinimumHeight(60)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    text-align: left;
                    padding-left: 15px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #3498db;
                }
            """)
            btn.clicked.connect(callback)
            actions_grid.addWidget(btn, i // 2, i % 2)
        
        actions_layout.addLayout(actions_grid)
        
        third_row.addWidget(processes_card, stretch=2)
        third_row.addWidget(actions_card, stretch=1)
        self.content_layout.addLayout(third_row)
        
        self.content_layout.addStretch()
    
    def setup_timers(self):
        """Настройка таймеров"""
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_dashboard)
        self.system_timer.start(2000)
    
    def update_dashboard(self):
        """Обновление данных на дашборде"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent()
            self.cpu_card.value_label.setText(f"{cpu_percent:.1f}%")
            
            # RAM
            ram = psutil.virtual_memory()
            self.ram_card.value_label.setText(f"{ram.percent:.1f}%")
            
            # Disk
            disk = psutil.disk_usage('C:/' if os.name == 'nt' else '/')
            self.disk_card.value_label.setText(f"{disk.percent:.1f}%")
            
            # Processes
            processes = len(psutil.pids())
            self.process_card.value_label.setText(str(processes))
            
        except Exception as e:
            print(f"Dashboard update error: {e}")
    
    def update_processes(self):
        """Обновление списка процессов"""
        self.processes_list.clear()
        try:
            for proc in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']), 
                             key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:10]:
                info = proc.info
                name = info['name'][:25]
                cpu = info['cpu_percent'] or 0
                memory = info['memory_percent'] or 0
                
                item = QListWidgetItem(f"{name} | CPU: {cpu:.1f}% | RAM: {memory:.2f}%")
                self.processes_list.addItem(item)
        except:
            pass
    
    def update_status_indicator(self):
        """Обновление индикатора статуса"""
        if self.raven.is_listening:
            self.status_indicator.setText("🔊")
            self.status_indicator.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
        else:
            self.status_indicator.setText("🔈")
            self.status_indicator.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
    
    def on_nav_clicked(self):
        """Обработка клика по навигации"""
        sender = self.sender()
        for btn in self.nav_buttons:
            btn.setChecked(btn is sender)
        
        # Обновляем заголовок
        page_titles = {
            "dashboard": "Dashboard",
            "voice": "Voice Control",
            "system": "System Monitor",
            "analytics": "Analytics",
            "ai": "AI Assistant",
            "actions": "Quick Actions",
            "settings": "Settings",
            "help": "Help"
        }
        self.page_title.setText(page_titles.get(sender.objectName(), "Dashboard"))
    
    def toggle_assistant_status(self):
        """Переключение статуса ассистента"""
        if self.raven.is_listening:
            self.raven.is_listening = False
            self.add_chat_message("System", "Voice assistant stopped", False)
        else:
            self.raven.is_listening = True
            self.add_chat_message("System", "Voice assistant activated", False)
            threading.Thread(target=self.raven._listening_loop, daemon=True).start()
        
        self.update_status_indicator()
    
    def start_voice_input(self):
        """Запуск голосового ввода"""
        self.add_chat_message("You", "Listening...", True)
        
        def listen():
            try:
                if hasattr(self.raven, 'listen'):
                    text = self.raven.listen(timeout=10)
                    if text:
                        self.add_chat_message("You", text, True)
                        response = self.raven.process_command(text)
                        if isinstance(response, dict):
                            self.add_chat_message("Raven", response['response'], False)
                        else:
                            self.add_chat_message("Raven", response, False)
                    else:
                        self.add_chat_message("System", "No speech detected", False)
            except Exception as e:
                self.add_chat_message("System", f"Error: {str(e)}", False)
        
        threading.Thread(target=listen, daemon=True).start()
    
    def start_voice_command(self):
        """Запуск голосовой команды"""
        self.start_voice_input()
    
    def send_chat_message(self):
        """Отправка текстового сообщения"""
        text = self.chat_input.text().strip()
        if not text:
            return
        
        self.add_chat_message("You", text, True)
        self.chat_input.clear()
        
        # Обработка команды
        try:
            response = self.raven.process_command(text)
            if isinstance(response, dict):
                self.add_chat_message("Raven", response['response'], False)
            else:
                self.add_chat_message("Raven", response, False)
        except Exception as e:
            self.add_chat_message("System", f"Error: {str(e)}", False)
    
    def add_chat_message(self, sender, text, is_user):
        """Добавление сообщения в чат"""
        timestamp = time.strftime("%H:%M")
        message_widget = ChatMessage(text, is_user, timestamp)
        
        # Удаляем stretch, добавляем сообщение, затем снова stretch
        self.chat_layout.removeItem(self.chat_layout.itemAt(self.chat_layout.count() - 1))
        self.chat_layout.addWidget(message_widget)
        self.chat_layout.addStretch()
        
        # Прокрутка вниз
        QTimer.singleShot(100, self.scroll_chat_to_bottom)
    
    def scroll_chat_to_bottom(self):
        """Прокрутка чата вниз"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def load_chat_history(self):
        """Загрузка истории чата"""
        # Загрузка из файла или базы данных
        welcome_msg = "Hello! I'm Raven AI, your personal assistant. How can I help you today?"
        self.add_chat_message("Raven", welcome_msg, False)
    
    def open_browser(self):
        """Открыть браузер"""
        import webbrowser
        webbrowser.open("https://www.google.com")
        self.add_chat_message("System", "Opening browser...", False)
    
    def show_system_info(self):
        """Показать информацию о системе"""
        try:
            import platform
            info = f"""
System: {platform.system()} {platform.release()}
CPU Cores: {psutil.cpu_count()}
Total RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB
Disk Space: {psutil.disk_usage('C:/' if os.name == 'nt' else '/').total / (1024**3):.1f} GB
"""
            self.add_chat_message("System", info.strip(), False)
        except Exception as e:
            self.add_chat_message("System", f"Error getting system info: {e}", False)
    
    def clean_ram(self):
        """Очистка RAM (имитация)"""
        import gc
        gc.collect()
        self.add_chat_message("System", "RAM cleanup initiated", False)
    
    def take_screenshot(self):
        """Сделать скриншот"""
        try:
            from PIL import ImageGrab
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            ImageGrab.grab().save(filename)
            self.add_chat_message("System", f"Screenshot saved as {filename}", False)
        except:
            self.add_chat_message("System", "Failed to take screenshot", False)
    
    def open_settings(self):
        """Открыть настройки"""
        self.add_chat_message("System", "Opening settings...", False)
    
    def mousePressEvent(self, event):
        """Перетаскивание окна"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Перетаскивание окна"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_pos'):
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()