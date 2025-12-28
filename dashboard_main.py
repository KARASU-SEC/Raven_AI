"""
Главное окно Raven AI Dashboard с боковой панелью и переключением страниц
"""
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QStackedWidget,
                             QScrollArea, QSizePolicy, QLineEdit)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

# Импортируем страницы
from ui.pages.dashboard_page import DashboardPage
from ui.pages.voice_page import VoicePage
from ui.pages.system_page import SystemPage
from ui.pages.ai_page import AIPage
from ui.pages.settings_page import SettingsPage


class NavButton(QPushButton):
    """Кастомная кнопка навигации"""
    
    def __init__(self, icon, text, page_id):
        super().__init__(f"  {icon}  {text}")
        self.page_id = page_id
        self.is_active = False
        
        self.update_style()
    
    def set_active(self, active):
        """Установка активного состояния"""
        if self.is_active != active:
            self.is_active = active
            self.update_style()
    
    def update_style(self):
        """Обновление стиля кнопки"""
        if self.is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    text-align: left;
                    padding-left: 25px;
                    font-size: 14px;
                    font-weight: 500;
                    border-radius: 0px;
                    border-left: 4px solid #2980b9;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
        else:
            self.setStyleSheet("""
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
            """)


class DashboardMainWindow(QMainWindow):
    """Главное окно дашборда с навигацией"""
    
    def __init__(self, raven_ai):
        super().__init__()
        self.raven = raven_ai
        self.pages = {}
        
        self.setWindowTitle("Raven AI Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)
        
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
        
        # Контейнер страниц
        self.stacked_widget = QStackedWidget()
        main_content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(main_content, stretch=1)
        
        # Инициализация страниц
        self.init_pages()
        
        # Показываем первую страницу
        self.show_page('dashboard')
    
    def create_sidebar(self):
        """Создание боковой панели навигации"""
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Логотип и заголовок
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
        layout.addWidget(logo_frame)
        
        # Навигационные кнопки
        self.nav_buttons = []
        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("🎤", "Voice Control", "voice"),
            ("⚙️", "System Monitor", "system"),
            ("🤖", "AI Assistant", "ai"),
            ("🔧", "Settings", "settings")
        ]
        
        for icon, text, page_id in nav_items:
            btn = NavButton(icon, text, page_id)
            btn.clicked.connect(lambda checked, p=page_id: self.show_page(p))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
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
        user_name = QLabel("User Admin")
        user_name.setStyleSheet("""
            color: #ecf0f1;
            font-weight: 600;
            font-size: 14px;
        """)
        user_role = QLabel("Administrator")
        user_role.setStyleSheet("""
            color: #95a5a6;
            font-size: 12px;
        """)
        user_info.addWidget(user_name)
        user_info.addWidget(user_role)
        
        profile_layout.addWidget(avatar)
        profile_layout.addLayout(user_info)
        layout.addWidget(profile_frame)
        
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
        
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(25, 0, 25, 0)
        
        # Заголовок текущей страницы
        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 22px;
                font-weight: 700;
            }
        """)
        layout.addWidget(self.page_title)
        
        layout.addStretch()
        
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
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search commands, settings...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                font-size: 14px;
                color: #2c3e50;
            }
        """)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_frame)
        
        # Кнопка уведомлений
        self.notif_btn = QPushButton("🔔")
        self.notif_btn.setFixedSize(40, 40)
        self.notif_btn.setStyleSheet("""
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
        
        # Статус голоса
        self.voice_status_btn = QPushButton("🔊 Active")
        self.voice_status_btn.setCheckable(True)
        self.voice_status_btn.setChecked(True)
        self.voice_status_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:checked {
                background-color: #2ecc71;
            }
            QPushButton:unchecked {
                background-color: #e74c3c;
            }
        """)
        self.voice_status_btn.clicked.connect(self.toggle_voice_status)
        
        layout.addWidget(self.notif_btn)
        layout.addWidget(self.voice_status_btn)
        
        return topbar
    
    def init_pages(self):
        """Инициализация всех страниц"""
        # Создаем страницы
        self.pages['dashboard'] = DashboardPage(self.raven)
        self.pages['voice'] = VoicePage(self.raven)
        self.pages['system'] = SystemPage(self.raven)
        self.pages['ai'] = AIPage(self.raven)
        self.pages['settings'] = SettingsPage(self.raven)
        
        # Добавляем в stacked widget
        for page_id, page in self.pages.items():
            self.stacked_widget.addWidget(page)
    
    def show_page(self, page_id):
        """Показать выбранную страницу"""
        if page_id in self.pages:
            # Обновляем заголовок
            titles = {
                'dashboard': 'Dashboard',
                'voice': 'Voice Control',
                'system': 'System Monitor',
                'ai': 'AI Assistant',
                'settings': 'Settings'
            }
            self.page_title.setText(titles.get(page_id, 'Dashboard'))
            
            # Переключаем страницу
            self.stacked_widget.setCurrentWidget(self.pages[page_id])
            
            # Обновляем активную кнопку навигации
            for btn in self.nav_buttons:
                btn.set_active(btn.page_id == page_id)
    
    def toggle_voice_status(self):
        """Переключение статуса голоса"""
        self.raven.is_voice_active = self.voice_status_btn.isChecked()
        status = "enabled" if self.raven.is_voice_active else "disabled"
        
        # Уведомляем текущую страницу
        current_page = self.stacked_widget.currentWidget()
        if hasattr(current_page, 'show_notification'):
            current_page.show_notification(f"Voice {status}")
        
        # Озвучиваем
        self.raven.speak(f"Voice {status}")
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        # Останавливаем все таймеры на страницах
        for page in self.pages.values():
            if hasattr(page, 'cleanup'):
                page.cleanup()
        
        # Останавливаем TTS
        self.raven.tts_engine.stop()
        
        event.accept()