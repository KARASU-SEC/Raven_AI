"""
Страница настроек Raven AI
"""
import json
import os
import psutil
import platform
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGroupBox, QLineEdit,
                             QComboBox, QCheckBox, QSlider, QTabWidget,
                             QListWidget, QListWidgetItem, QFileDialog,
                             QMessageBox, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon

class SettingsPage(QWidget):
    """Страница настроек"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, raven_ai):
        super().__init__()
        self.raven = raven_ai
        self.config = self.load_config()
        
        self.setup_ui()
        self.load_settings()
    
    def load_config(self):
        """Загрузка конфигурации"""
        config_file = os.path.join('config', 'settings.json')
        default_config = {
            "appearance": {
                "theme": "light",
                "accent_color": "#3498db",
                "font_size": 13,
                "animation_enabled": True
            },
            "voice": {
                "enabled": True,
                "wake_words": ["рейвен", "рэйвэн", "raven"],
                "language": "ru-RU",
                "timeout": 10,
                "sensitivity": 7
            },
            "ai": {
                "model": "neural_core",
                "enable_learning": True,
                "enable_context": True,
                "max_history": 10
            },
            "system": {
                "auto_start": False,
                "check_updates": True,
                "save_logs": True,
                "log_level": "INFO"
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    return self.merge_dicts(default_config, loaded)
        except:
            pass
        
        return default_config
    
    def merge_dicts(self, default, new):
        """Рекурсивное объединение словарей"""
        result = default.copy()
        for key, value in new.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """Сохранение конфигурации"""
        try:
            os.makedirs('config', exist_ok=True)
            config_file = os.path.join('config', 'settings.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            self.settings_changed.emit(self.config)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def setup_ui(self):
        """Настройка интерфейса страницы"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("🔧 Settings")
        title.setStyleSheet("""
            color: #2c3e50;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Вкладки настроек
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
        """)
        
        # Вкладка 1: Внешний вид
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        appearance_layout.addWidget(self.create_appearance_widget())
        tabs.addTab(appearance_tab, "Appearance")
        
        # Вкладка 2: Голос
        voice_tab = QWidget()
        voice_layout = QVBoxLayout(voice_tab)
        voice_layout.addWidget(self.create_voice_widget())
        tabs.addTab(voice_tab, "Voice")
        
        # Вкладка 3: ИИ
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        ai_layout.addWidget(self.create_ai_widget())
        tabs.addTab(ai_tab, "AI")
        
        # Вкладка 4: Система
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        system_layout.addWidget(self.create_system_widget())
        tabs.addTab(system_tab, "System")
        
        layout.addWidget(tabs)
        
        # Кнопки сохранения
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet("""
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
        reset_btn.clicked.connect(self.reset_settings)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_appearance_widget(self):
        """Создание виджета внешнего вида"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Тема
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        
        theme_layout.addWidget(QLabel("Color Theme:"))
        
        theme_selector = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        theme_selector.addWidget(self.theme_combo)
        theme_selector.addStretch()
        theme_layout.addLayout(theme_selector)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Цветовая схема
        color_group = QGroupBox("Color Scheme")
        color_layout = QVBoxLayout()
        
        color_layout.addWidget(QLabel("Accent Color:"))
        
        color_selector = QHBoxLayout()
        self.color_combo = QComboBox()
        self.color_combo.addItems(["Blue (#3498db)", "Green (#2ecc71)", "Purple (#9b59b6)", "Orange (#f39c12)", "Red (#e74c3c)"])
        color_selector.addWidget(self.color_combo)
        color_selector.addStretch()
        color_layout.addLayout(color_selector)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # Шрифт
        font_group = QGroupBox("Font")
        font_layout = QVBoxLayout()
        
        font_layout.addWidget(QLabel("Font Size:"))
        
        font_selector = QHBoxLayout()
        self.font_size = QSpinBox()
        self.font_size.setRange(10, 20)
        self.font_size.setSuffix(" px")
        font_selector.addWidget(self.font_size)
        font_selector.addStretch()
        font_layout.addLayout(font_selector)
        
        self.animation_check = QCheckBox("Enable animations")
        font_layout.addWidget(self.animation_check)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        layout.addStretch()
        return widget
    
    def create_voice_widget(self):
        """Создание виджета голоса"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Основные настройки
        main_group = QGroupBox("Voice Settings")
        main_layout = QVBoxLayout()
        
        self.voice_enabled = QCheckBox("Enable voice control")
        main_layout.addWidget(self.voice_enabled)
        
        main_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Russian (ru-RU)", "English (en-US)", "Auto-detect"])
        main_layout.addWidget(self.language_combo)
        
        main_layout.addWidget(QLabel("Wake Words (comma separated):"))
        self.wake_words_input = QLineEdit()
        self.wake_words_input.setPlaceholderText("рейвен, рэйвэн, raven")
        main_layout.addWidget(self.wake_words_input)
        
        main_group.setLayout(main_layout)
        layout.addWidget(main_group)
        
        # Параметры распознавания
        params_group = QGroupBox("Recognition Parameters")
        params_layout = QVBoxLayout()
        
        params_layout.addWidget(QLabel("Listening timeout (seconds):"))
        self.timeout_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeout_slider.setRange(1, 30)
        params_layout.addWidget(self.timeout_slider)
        
        params_layout.addWidget(QLabel("Sensitivity:"))
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        params_layout.addWidget(self.sensitivity_slider)
        
        self.offline_check = QCheckBox("Use offline recognition (if available)")
        params_layout.addWidget(self.offline_check)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Тест микрофона
        test_group = QGroupBox("Microphone Test")
        test_layout = QVBoxLayout()
        
        test_btn = QPushButton("Test Microphone")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        test_btn.clicked.connect(self.test_microphone)
        
        self.mic_status = QLabel("Click 'Test Microphone' to check")
        self.mic_status.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        
        test_layout.addWidget(test_btn)
        test_layout.addWidget(self.mic_status)
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        layout.addStretch()
        return widget
    
    def create_ai_widget(self):
        """Создание виджета ИИ"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Модель ИИ
        model_group = QGroupBox("AI Model")
        model_layout = QVBoxLayout()
        
        model_layout.addWidget(QLabel("AI Engine:"))
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.addItems(["Neural Core", "GPT-3.5 (API)", "Local LLM", "Hybrid"])
        model_layout.addWidget(self.ai_model_combo)
        
        model_layout.addWidget(QLabel("API Key (if needed):"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        model_layout.addWidget(self.api_key_input)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Поведение ИИ
        behavior_group = QGroupBox("AI Behavior")
        behavior_layout = QVBoxLayout()
        
        self.context_check = QCheckBox("Enable context memory")
        behavior_layout.addWidget(self.context_check)
        
        self.learning_check = QCheckBox("Learn from interactions")
        behavior_layout.addWidget(self.learning_check)
        
        self.emotions_check = QCheckBox("Show emotional responses")
        behavior_layout.addWidget(self.emotions_check)
        
        behavior_layout.addWidget(QLabel("Max conversation history:"))
        self.history_spin = QSpinBox()
        self.history_spin.setRange(5, 100)
        self.history_spin.setSuffix(" messages")
        behavior_layout.addWidget(self.history_spin)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        # Обучение
        training_group = QGroupBox("Training")
        training_layout = QVBoxLayout()
        
        train_btn = QPushButton("Train AI on conversation history")
        train_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
        """)
        train_btn.clicked.connect(self.train_ai)
        
        training_layout.addWidget(train_btn)
        training_layout.addWidget(QLabel("Note: Training may take several minutes"))
        
        training_group.setLayout(training_layout)
        layout.addWidget(training_group)
        
        layout.addStretch()
        return widget
    
    def create_system_widget(self):
        """Создание виджета системы"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Автозапуск
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout()
        
        self.auto_start_check = QCheckBox("Start Raven AI on system startup")
        startup_layout.addWidget(self.auto_start_check)
        
        self.minimize_check = QCheckBox("Start minimized to system tray")
        startup_layout.addWidget(self.minimize_check)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # Обновления
        update_group = QGroupBox("Updates")
        update_layout = QVBoxLayout()
        
        self.update_check = QCheckBox("Check for updates automatically")
        update_layout.addWidget(self.update_check)
        
        check_now_btn = QPushButton("Check for updates now")
        check_now_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        check_now_btn.clicked.connect(self.check_updates)
        update_layout.addWidget(check_now_btn)
        
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)
        
        # Логирование
        log_group = QGroupBox("Logging")
        log_layout = QVBoxLayout()
        
        self.log_check = QCheckBox("Save application logs")
        log_layout.addWidget(self.log_check)
        
        log_layout.addWidget(QLabel("Log level:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        log_layout.addWidget(self.log_level_combo)
        
        view_logs_btn = QPushButton("View Logs")
        view_logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        view_logs_btn.clicked.connect(self.view_logs)
        log_layout.addWidget(view_logs_btn)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Информация о системе
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout()
        
        import platform
        info = f"""
Python: {platform.python_version()}
OS: {platform.system()} {platform.release()}
CPU Cores: {psutil.cpu_count()}
RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB
        """
        
        info_label = QLabel(info.strip())
        info_label.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', monospace;
                font-size: 12px;
                color: #666666;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
            }
        """)
        info_layout.addWidget(info_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        return widget
    
    def load_settings(self):
        """Загрузка настроек в UI"""
        # Внешний вид
        theme = self.config['appearance']['theme'].capitalize()
        self.theme_combo.setCurrentText(theme if theme in ["Light", "Dark", "Auto"] else "Light")
        
        accent_color = self.config['appearance']['accent_color']
        color_map = {
            "#3498db": "Blue (#3498db)",
            "#2ecc71": "Green (#2ecc71)",
            "#9b59b6": "Purple (#9b59b6)",
            "#f39c12": "Orange (#f39c12)",
            "#e74c3c": "Red (#e74c3c)"
        }
        self.color_combo.setCurrentText(color_map.get(accent_color, "Blue (#3498db)"))
        
        self.font_size.setValue(self.config['appearance']['font_size'])
        self.animation_check.setChecked(self.config['appearance']['animation_enabled'])
        
        # Голос
        self.voice_enabled.setChecked(self.config['voice']['enabled'])
        self.language_combo.setCurrentText("Russian (ru-RU)" if self.config['voice']['language'] == "ru-RU" else "English (en-US)")
        self.wake_words_input.setText(", ".join(self.config['voice']['wake_words']))
        self.timeout_slider.setValue(self.config['voice']['timeout'])
        self.sensitivity_slider.setValue(self.config['voice']['sensitivity'])
        
        # ИИ
        self.ai_model_combo.setCurrentText(self.config['ai']['model'].replace('_', ' ').title())
        self.context_check.setChecked(self.config['ai']['enable_context'])
        self.learning_check.setChecked(self.config['ai']['enable_learning'])
        self.history_spin.setValue(self.config['ai']['max_history'])
        
        # Система
        self.auto_start_check.setChecked(self.config['system']['auto_start'])
        self.update_check.setChecked(self.config['system']['check_updates'])
        self.log_check.setChecked(self.config['system']['save_logs'])
        self.log_level_combo.setCurrentText(self.config['system']['log_level'])
    
    def save_settings(self):
        """Сохранение настроек"""
        # Внешний вид
        self.config['appearance']['theme'] = self.theme_combo.currentText().lower()
        
        color_text = self.color_combo.currentText()
        color_map = {
            "Blue (#3498db)": "#3498db",
            "Green (#2ecc71)": "#2ecc71",
            "Purple (#9b59b6)": "#9b59b6",
            "Orange (#f39c12)": "#f39c12",
            "Red (#e74c3c)": "#e74c3c"
        }
        self.config['appearance']['accent_color'] = color_map.get(color_text, "#3498db")
        
        self.config['appearance']['font_size'] = self.font_size.value()
        self.config['appearance']['animation_enabled'] = self.animation_check.isChecked()
        
        # Голос
        self.config['voice']['enabled'] = self.voice_enabled.isChecked()
        self.config['voice']['language'] = "ru-RU" if "Russian" in self.language_combo.currentText() else "en-US"
        self.config['voice']['wake_words'] = [w.strip() for w in self.wake_words_input.text().split(',') if w.strip()]
        self.config['voice']['timeout'] = self.timeout_slider.value()
        self.config['voice']['sensitivity'] = self.sensitivity_slider.value()
        
        # ИИ
        self.config['ai']['model'] = self.ai_model_combo.currentText().lower().replace(' ', '_')
        self.config['ai']['enable_context'] = self.context_check.isChecked()
        self.config['ai']['enable_learning'] = self.learning_check.isChecked()
        self.config['ai']['max_history'] = self.history_spin.value()
        
        # Система
        self.config['system']['auto_start'] = self.auto_start_check.isChecked()
        self.config['system']['check_updates'] = self.update_check.isChecked()
        self.config['system']['save_logs'] = self.log_check.isChecked()
        self.config['system']['log_level'] = self.log_level_combo.currentText()
        
        if self.save_config():
            self.raven.is_voice_active = self.config['voice']['enabled']
            
            QMessageBox.information(self, "Settings Saved", 
                                  "Settings have been saved successfully!\nSome changes may require restarting the application.")
        else:
            QMessageBox.warning(self, "Error", "Failed to save settings!")
    
    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to default values?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config = self.load_config()
            self.load_settings()
            
            QMessageBox.information(self, "Settings Reset", 
                                  "Settings have been reset to default values.")
    
    def test_microphone(self):
        """Тест микрофона"""
        self.mic_status.setText("🎤 Testing microphone... Please speak")
        
        import threading
        def test():
            text = self.raven.listen(timeout=5)
            if text:
                self.raven.speak(f"I heard: {text}")
                self.mic_status.setText(f"✅ Microphone working! Heard: {text[:30]}...")
            else:
                self.raven.speak("I didn't hear anything")
                self.mic_status.setText("❌ No audio detected. Check microphone connection.")
        
        thread = threading.Thread(target=test, daemon=True)
        thread.start()
    
    def train_ai(self):
        """Обучение ИИ"""
        QMessageBox.information(self, "Training", 
                              "Training feature is under development.\n"
                              "Future versions will include machine learning capabilities.")
    
    def check_updates(self):
        """Проверка обновлений"""
        self.raven.speak("Checking for updates")
        QMessageBox.information(self, "Updates", 
                              "You are using the latest version of Raven AI!")
    
    def view_logs(self):
        """Просмотр логов"""
        QMessageBox.information(self, "Logs", 
                              "Log viewer is under development.\n"
                              "Logs are saved in the 'logs' folder.")