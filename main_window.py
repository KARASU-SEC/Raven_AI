"""
Главное окно Raven AI
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTextEdit, QLineEdit,
                             QFrame, QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
import threading
import time

class RavenMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raven AI - Голосовой ассистент")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ========== ШАПКА ==========
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Логотип и название
        logo_label = QLabel("🦅")
        logo_label.setFont(QFont("Segoe UI Emoji", 36))
        
        title_label = QLabel("Raven AI")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #4dabf7;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Статус
        self.status_label = QLabel("🔄 Инициализация...")
        self.status_label.setStyleSheet("color: #adb5bd; font-weight: bold;")
        header_layout.addWidget(self.status_label)
        
        main_layout.addWidget(header_frame)
        
        # ========== ОСНОВНОЕ СОДЕРЖИМОЕ ==========
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Левая панель - Лог и управление
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        left_panel.setFixedWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Лог команд
        log_label = QLabel("📝 История команд:")
        log_label.setStyleSheet("color: #4dabf7; font-weight: bold;")
        left_layout.addWidget(log_label)
        
        self.command_log = QTextEdit()
        self.command_log.setReadOnly(True)
        self.command_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #495057;
                border-radius: 8px;
                padding: 10px;
                color: #e9ecef;
                font-family: 'Consolas', monospace;
                font-size: 11pt;
            }
        """)
        self.command_log.setMaximumHeight(300)
        left_layout.addWidget(self.command_log)
        
        # Панель управления
        control_label = QLabel("⚡ Управление:")
        control_label.setStyleSheet("color: #4dabf7; font-weight: bold;")
        left_layout.addWidget(control_label)
        
        # Кнопки управления
        self.mic_button = QPushButton("🎤 Тест микрофона")
        self.mic_button.clicked.connect(self.test_microphone)
        self.mic_button.setFixedHeight(45)
        
        self.listen_button = QPushButton("👂 Слушать команду")
        self.listen_button.clicked.connect(self.listen_command)
        self.listen_button.setFixedHeight(45)
        
        self.sys_button = QPushButton("💻 Инфо системы")
        self.sys_button.clicked.connect(self.show_system_info)
        self.sys_button.setFixedHeight(45)
        
        left_layout.addWidget(self.mic_button)
        left_layout.addWidget(self.listen_button)
        left_layout.addWidget(self.sys_button)
        left_layout.addStretch()
        
        # Правая панель - Информация и ввод
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        
        # Отображение информации
        info_label = QLabel("📄 Информация:")
        info_label.setStyleSheet("color: #4dabf7; font-weight: bold;")
        right_layout.addWidget(info_label)
        
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #495057;
                border-radius: 8px;
                padding: 15px;
                color: #e9ecef;
                font-family: 'Consolas', monospace;
                font-size: 11pt;
                line-height: 1.4;
            }
        """)
        right_layout.addWidget(self.info_display)
        
        # Ввод команды
        input_label = QLabel("⌨️ Ввод команды:")
        input_label.setStyleSheet("color: #4dabf7; font-weight: bold;")
        right_layout.addWidget(input_label)
        
        input_layout = QHBoxLayout()
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Введите команду...")
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                border: 2px solid #495057;
                border-radius: 8px;
                padding: 10px;
                color: #e9ecef;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #4dabf7;
            }
        """)
        self.command_input.returnPressed.connect(self.process_command)
        
        send_button = QPushButton("▶️")
        send_button.setFixedWidth(50)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #4dabf7;
                border: none;
                border-radius: 8px;
                padding: 10px;
                color: #1e1e1e;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #339af0;
            }
        """)
        send_button.clicked.connect(self.process_command)
        
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(send_button)
        right_layout.addLayout(input_layout)
        
        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)
        main_layout.addWidget(content_widget, stretch=1)
        
        # ========== ПОДВАЛ ==========
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        footer_layout = QHBoxLayout(footer_frame)
        
        self.cpu_label = QLabel("CPU: --%")
        self.ram_label = QLabel("RAM: --%")
        
        for label in [self.cpu_label, self.ram_label]:
            label.setStyleSheet("color: #adb5bd; font-size: 10pt;")
            footer_layout.addWidget(label)
        
        footer_layout.addStretch()
        
        version_label = QLabel("Raven AI v1.0")
        version_label.setStyleSheet("color: #868e96; font-size: 10pt;")
        footer_layout.addWidget(version_label)
        
        main_layout.addWidget(footer_frame)
        
        # Таймер обновления системной информации
        self.sys_info_timer = QTimer()
        self.sys_info_timer.timeout.connect(self.update_system_indicators)
        self.sys_info_timer.start(2000)
        
        # Инициализация компонентов
        QTimer.singleShot(100, self.initialize_components)
    
    def initialize_components(self):
        """Инициализация компонентов Raven AI"""
        try:
            from core.voice_engine.voice_processor import VoiceCommandProcessor
            
            self.processor = VoiceCommandProcessor()
            self.status_label.setText("✅ Raven AI готов к работе!")
            self.log("Система инициализирована")
            
        except Exception as e:
            self.status_label.setText("❌ Ошибка инициализации")
            self.log(f"Ошибка: {str(e)}")
    
    def log(self, message):
        """Добавление сообщения в лог"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        self.command_log.append(f"[{timestamp}] {message}")
        
        # Автопрокрутка
        scrollbar = self.command_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def test_microphone(self):
        """Тест микрофона"""
        self.log("Тестирую микрофон...")
        
        def test_in_thread():
            try:
                import speech_recognition as sr
                
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    self.log("Настраиваюсь на шум...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    self.log("Говорите что-нибудь...")
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    
                    try:
                        text = recognizer.recognize_google(audio, language='ru-RU')
                        self.log(f"✅ Распознано: '{text}'")
                        
                        # Озвучиваем ответ
                        if hasattr(self, 'processor'):
                            self.processor.tts.speak(f"Вы сказали: {text}")
                            
                    except sr.UnknownValueError:
                        self.log("❌ Не удалось распознать речь")
                    except sr.RequestError:
                        self.log("⚠️ Проблема с сервисом распознавания")
                        
            except Exception as e:
                self.log(f"❌ Ошибка: {e}")
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=test_in_thread)
        thread.start()
    
    def listen_command(self):
        """Прослушивание голосовой команды"""
        self.log("Слушаю команду...")
        
        def listen_in_thread():
            try:
                if hasattr(self, 'processor'):
                    self.processor.process_command(timeout_seconds=10)
                else:
                    self.log("❌ Процессор не инициализирован")
            except Exception as e:
                self.log(f"❌ Ошибка: {e}")
        
        thread = threading.Thread(target=listen_in_thread)
        thread.start()
    
    def show_system_info(self):
        """Показать информацию о системе"""
        try:
            import psutil
            
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            info = f"""📊 СИСТЕМНАЯ ИНФОРМАЦИЯ:
CPU: {cpu}%
RAM: {ram}%
Процессов: {len(psutil.pids())}
            """
            
            self.info_display.setText(info.strip())
            self.log("Получена системная информация")
            
            # Озвучиваем
            if hasattr(self, 'processor'):
                self.processor.tts.speak(f"ЦПУ: {cpu} процентов, память: {ram} процентов")
                
        except Exception as e:
            self.log(f"❌ Ошибка: {e}")
    
    def process_command(self):
        """Обработать текстовую команду"""
        command = self.command_input.text().strip()
        if not command:
            return
            
        self.log(f"Команда: {command}")
        self.command_input.clear()
        
        # Обработка команды
        if hasattr(self, 'processor'):
            result = self.processor.process_command_text(command)
            self.info_display.setText(f"📝 Результат:\n{result}")
        else:
            self.log("❌ Процессор не инициализирован")
    
    def update_system_indicators(self):
        """Обновление индикаторов системы в футере"""
        try:
            import psutil
            
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            self.cpu_label.setText(f"CPU: {cpu:.1f}%")
            self.ram_label.setText(f"RAM: {ram:.1f}%")
            
        except:
            pass