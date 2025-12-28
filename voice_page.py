"""
Страница голосового управления
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGroupBox, QCheckBox,
                             QSlider, QComboBox, QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class VoicePage(QWidget):
    """Страница управления голосом"""
    
    voice_status_changed = pyqtSignal(bool)
    
    def __init__(self, raven_ai):
        super().__init__()
        self.raven = raven_ai
        self.is_listening = False
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса страницы"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("🎤 Voice Control")
        title.setStyleSheet("""
            color: #2c3e50;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Основной контент в два столбца
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Левая колонка: настройки
        left_column = QVBoxLayout()
        left_column.setSpacing(20)
        
        # Настройки активации
        activation_group = QGroupBox("Wake Word Settings")
        activation_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        activation_layout = QVBoxLayout()
        
        # Wake words
        wake_words_label = QLabel("Wake Words (comma separated):")
        self.wake_words_input = QTextEdit()
        self.wake_words_input.setPlainText("рейвен, рэйвэн, raven")
        self.wake_words_input.setMaximumHeight(60)
        self.wake_words_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        
        # Чувствительность
        sensitivity_label = QLabel("Sensitivity:")
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(7)
        
        # Автоактивация
        self.auto_activate_check = QCheckBox("Auto-activate on wake word")
        self.auto_activate_check.setChecked(True)
        
        activation_layout.addWidget(wake_words_label)
        activation_layout.addWidget(self.wake_words_input)
        activation_layout.addWidget(sensitivity_label)
        activation_layout.addWidget(self.sensitivity_slider)
        activation_layout.addWidget(self.auto_activate_check)
        
        activation_group.setLayout(activation_layout)
        left_column.addWidget(activation_group)
        
        # Настройки распознавания
        recognition_group = QGroupBox("Speech Recognition")
        recognition_layout = QVBoxLayout()
        
        # Язык
        language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Russian", "Auto-detect"])
        self.language_combo.setCurrentText("Russian")
        
        # Таймаут
        timeout_label = QLabel("Listening timeout (seconds):")
        self.timeout_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeout_slider.setRange(1, 30)
        self.timeout_slider.setValue(10)
        
        # Офлайн режим
        self.offline_mode_check = QCheckBox("Use offline recognition")
        self.offline_mode_check.setChecked(False)
        
        recognition_layout.addWidget(language_label)
        recognition_layout.addWidget(self.language_combo)
        recognition_layout.addWidget(timeout_label)
        recognition_layout.addWidget(self.timeout_slider)
        recognition_layout.addWidget(self.offline_mode_check)
        
        recognition_group.setLayout(recognition_layout)
        left_column.addWidget(recognition_group)
        
        # Правая колонка: управление и тестирование
        right_column = QVBoxLayout()
        right_column.setSpacing(20)
        
        # Статус и управление
        status_group = QGroupBox("Voice Status & Control")
        status_layout = QVBoxLayout()
        
        # Индикатор состояния
        self.status_indicator = QLabel("🔈 Voice Inactive")
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #ffeaea;
                border-radius: 8px;
                text-align: center;
            }
        """)
        
        # Кнопки управления
        control_layout = QHBoxLayout()
        
        self.toggle_btn = QPushButton("🎤 Start Listening")
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_listening)
        
        self.test_mic_btn = QPushButton("Test Microphone")
        self.test_mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        self.test_mic_btn.clicked.connect(self.test_microphone)
        
        control_layout.addWidget(self.toggle_btn)
        control_layout.addWidget(self.test_mic_btn)
        
        status_layout.addWidget(self.status_indicator)
        status_layout.addLayout(control_layout)
        status_group.setLayout(status_layout)
        right_column.addWidget(status_group)
        
        # Тестирование голоса
        test_group = QGroupBox("Voice Test")
        test_layout = QVBoxLayout()
        
        test_input = QTextEdit()
        test_input.setPlaceholderText("Type text to test voice synthesis...")
        test_input.setMaximumHeight(80)
        test_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        
        test_btn = QPushButton("Test Voice Synthesis")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        test_btn.clicked.connect(lambda: self.raven.speak(test_input.toPlainText()))
        
        test_layout.addWidget(test_input)
        test_layout.addWidget(test_btn)
        test_group.setLayout(test_layout)
        right_column.addWidget(test_group)
        
        # История команд
        history_group = QGroupBox("Recent Commands")
        history_layout = QVBoxLayout()
        
        self.commands_list = QTextEdit()
        self.commands_list.setReadOnly(True)
        self.commands_list.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px;
                background-color: #f8f9fa;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        self.commands_list.setMinimumHeight(150)
        
        clear_btn = QPushButton("Clear History")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        clear_btn.clicked.connect(self.clear_history)
        
        history_layout.addWidget(self.commands_list)
        history_layout.addWidget(clear_btn)
        history_group.setLayout(history_layout)
        right_column.addWidget(history_group)
        
        content_layout.addLayout(left_column, stretch=1)
        content_layout.addLayout(right_column, stretch=1)
        layout.addLayout(content_layout)
        
        # Обновляем историю команд
        self.update_command_history()
    
    def toggle_listening(self):
        """Переключение режима прослушивания"""
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.toggle_btn.setText("⏸️ Stop Listening")
            self.status_indicator.setText("🔊 Voice Active - Listening...")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    color: #2ecc71;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    background-color: #e8f8f0;
                    border-radius: 8px;
                    text-align: center;
                }
            """)
            
            import threading
            thread = threading.Thread(target=self.listen_loop, daemon=True)
            thread.start()
        else:
            self.toggle_btn.setText("🎤 Start Listening")
            self.status_indicator.setText("🔈 Voice Inactive")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    background-color: #ffeaea;
                    border-radius: 8px;
                    text-align: center;
                }
            """)
    
    def listen_loop(self):
        """Цикл прослушивания"""
        while self.is_listening:
            text = self.raven.listen(timeout=5)
            if text:
                wake_words = self.wake_words_input.toPlainText().split(',')
                if any(wake_word.strip().lower() in text.lower() for wake_word in wake_words):
                    self.raven.speak("Yes, I'm listening")
                    continue
                
                response = self.raven.process_command(text)
                
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, self.update_command_history)
    
    def test_microphone(self):
        """Тест микрофона"""
        self.status_indicator.setText("🎤 Testing microphone...")
        
        import threading
        def test():
            text = self.raven.listen(timeout=5)
            if text:
                self.raven.speak(f"I heard: {text}")
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self.status_indicator.setText(f"✅ Heard: {text[:50]}..."))
            else:
                self.raven.speak("I didn't hear anything")
                QTimer.singleShot(0, lambda: self.status_indicator.setText("❌ No audio detected"))
        
        thread = threading.Thread(target=test, daemon=True)
        thread.start()
    
    def update_command_history(self):
        """Обновление истории команд"""
        history_text = ""
        for i, cmd in enumerate(self.raven.command_history[-10:]):
            history_text += f"[{cmd['time']}] {cmd['command'][:50]}...\n"
            history_text += f"    → {cmd['response'][:50]}...\n\n"
        
        if not history_text:
            history_text = "No commands yet. Start speaking!"
        
        self.commands_list.setPlainText(history_text)
    
    def clear_history(self):
        """Очистка истории команд"""
        self.raven.command_history = []
        self.commands_list.clear()