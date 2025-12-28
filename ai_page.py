"""
Страница ИИ ассистента
"""
import json
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGroupBox, QTextEdit,
                             QLineEdit, QComboBox, QCheckBox, QListWidget,
                             QListWidgetItem, QSplitter, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class AIPage(QWidget):
    """Страница ИИ ассистента"""
    
    def __init__(self, raven_ai):
        super().__init__()
        self.raven = raven_ai
        self.conversations = []
        self.current_conversation = []
        
        self.setup_ui()
        self.load_conversations()
    
    def setup_ui(self):
        """Настройка интерфейса страницы"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("🤖 AI Assistant")
        title.setStyleSheet("""
            color: #2c3e50;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Разделитель на две колонки
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Левая колонка: история и настройки
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # История разговоров
        conv_group = QGroupBox("Conversation History")
        conv_layout = QVBoxLayout()
        
        self.conversation_list = QListWidget()
        self.conversation_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        self.conversation_list.itemClicked.connect(self.load_conversation)
        
        conv_buttons_layout = QHBoxLayout()
        new_conv_btn = QPushButton("New Chat")
        new_conv_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        new_conv_btn.clicked.connect(self.new_conversation)
        
        delete_conv_btn = QPushButton("Delete")
        delete_conv_btn.setStyleSheet("""
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
        delete_conv_btn.clicked.connect(self.delete_conversation)
        
        conv_buttons_layout.addWidget(new_conv_btn)
        conv_buttons_layout.addWidget(delete_conv_btn)
        conv_buttons_layout.addStretch()
        
        conv_layout.addWidget(self.conversation_list)
        conv_layout.addLayout(conv_buttons_layout)
        conv_group.setLayout(conv_layout)
        left_layout.addWidget(conv_group)
        
        # Настройки ИИ
        settings_group = QGroupBox("AI Settings")
        settings_layout = QVBoxLayout()
        
        # Модель
        model_layout = QHBoxLayout()
        model_label = QLabel("AI Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Neural Core v2.1", "GPT-3.5 (API)", "Local LLM", "Hybrid"])
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        settings_layout.addLayout(model_layout)
        
        # Параметры
        self.context_check = QCheckBox("Enable context memory")
        self.context_check.setChecked(True)
        settings_layout.addWidget(self.context_check)
        
        self.learning_check = QCheckBox("Enable learning from interactions")
        self.learning_check.setChecked(True)
        settings_layout.addWidget(self.learning_check)
        
        self.emotions_check = QCheckBox("Enable emotional responses")
        self.emotions_check.setChecked(True)
        settings_layout.addWidget(self.emotions_check)
        
        settings_group.setLayout(settings_layout)
        left_layout.addWidget(settings_group)
        
        # Статистика
        stats_group = QGroupBox("AI Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("Total conversations: 0\nTotal messages: 0")
        self.stats_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666666;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
            }
        """)
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        left_layout.addWidget(stats_group)
        
        left_layout.addStretch()
        
        # Правая колонка: чат
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # Заголовок текущего разговора
        self.chat_title = QLabel("New Conversation")
        self.chat_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 18px;
                font-weight: 700;
                padding: 10px 0;
            }
        """)
        right_layout.addWidget(self.chat_title)
        
        # Прокручиваемая область чата
        self.chat_scroll = QTextEdit()
        self.chat_scroll.setReadOnly(True)
        self.chat_scroll.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                background-color: white;
                font-size: 14px;
                min-height: 400px;
            }
        """)
        self.chat_scroll.setAcceptRichText(True)
        right_layout.addWidget(self.chat_scroll)
        
        # Панель ввода
        input_group = QGroupBox("Ask AI Assistant")
        input_layout = QVBoxLayout()
        
        # Быстрые запросы
        quick_queries = QHBoxLayout()
        queries = ["What's the weather?", "Tell me a joke", "System status", "Help"]
        for query in queries:
            btn = QPushButton(query)
            btn.setStyleSheet("""
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
            btn.clicked.connect(lambda checked, q=query: self.ask_ai(q))
            quick_queries.addWidget(btn)
        
        quick_queries.addStretch()
        input_layout.addLayout(quick_queries)
        
        # Поле ввода
        input_row = QHBoxLayout()
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Type your question here...")
        self.ai_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.ai_input.returnPressed.connect(self.send_ai_query)
        
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
        send_btn.clicked.connect(self.send_ai_query)
        
        voice_btn = QPushButton("🎤")
        voice_btn.setFixedSize(50, 50)
        voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                margin-left: 10px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        voice_btn.clicked.connect(self.voice_query)
        
        input_row.addWidget(self.ai_input)
        input_row.addWidget(send_btn)
        input_row.addWidget(voice_btn)
        input_layout.addLayout(input_row)
        
        input_group.setLayout(input_layout)
        right_layout.addWidget(input_group)
        
        # Статус ИИ
        status_layout = QHBoxLayout()
        status_label = QLabel("AI Status:")
        self.ai_status = QLabel("✅ Ready")
        self.ai_status.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-weight: 600;
                padding: 6px 12px;
                background-color: #e8f8f0;
                border-radius: 6px;
            }
        """)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.ai_status)
        status_layout.addStretch()
        
        right_layout.addLayout(status_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
        # Создаем новый разговор по умолчанию
        self.new_conversation()
    
    def load_conversations(self):
        """Загрузка истории разговоров"""
        try:
            conv_file = os.path.join('data', 'conversations.json')
            if os.path.exists(conv_file):
                with open(conv_file, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
                    self.update_conversation_list()
        except:
            self.conversations = []
    
    def save_conversations(self):
        """Сохранение разговоров"""
        try:
            os.makedirs('data', exist_ok=True)
            conv_file = os.path.join('data', 'conversations.json')
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving conversations: {e}")
    
    def update_conversation_list(self):
        """Обновление списка разговоров"""
        self.conversation_list.clear()
        for i, conv in enumerate(self.conversations[-20:]):  # Последние 20 разговоров
            title = conv.get('title', f"Conversation {i+1}")
            item = QListWidgetItem(f"{title} ({len(conv.get('messages', []))} messages)")
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.conversation_list.addItem(item)
        
        # Обновляем статистику
        total_messages = sum(len(conv.get('messages', [])) for conv in self.conversations)
        self.stats_label.setText(f"Total conversations: {len(self.conversations)}\nTotal messages: {total_messages}")
    
    def new_conversation(self):
        """Создание нового разговора"""
        self.current_conversation = []
        self.chat_title.setText("New Conversation")
        self.chat_scroll.clear()
        
        # Добавляем приветственное сообщение
        welcome = """
<div style='background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;'>
    <b>🤖 Raven AI:</b><br>
    Hello! I'm your AI assistant. I can help you with:
    <ul>
        <li>Answering questions</li>
        <li>Controlling your system</li>
        <li>Providing information</li>
        <li>And much more!</li>
    </ul>
    How can I assist you today?
</div>
"""
        self.chat_scroll.append(welcome)
        self.current_conversation.append({
            'role': 'assistant',
            'content': welcome
        })
    
    def load_conversation(self, item):
        """Загрузка выбранного разговора"""
        conv_index = item.data(Qt.ItemDataRole.UserRole)
        if 0 <= conv_index < len(self.conversations):
            conv = self.conversations[conv_index]
            self.current_conversation = conv.get('messages', [])
            self.chat_title.setText(conv.get('title', 'Conversation'))
            
            # Отображаем сообщения
            self.chat_scroll.clear()
            for msg in self.current_conversation:
                if msg['role'] == 'user':
                    self.chat_scroll.append(f"<div style='background-color: #e3f2fd; padding: 10px; border-radius: 8px; margin: 5px 0;'><b>You:</b> {msg['content']}</div>")
                else:
                    self.chat_scroll.append(f"<div style='background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin: 5px 0;'><b>🤖 Raven AI:</b> {msg['content']}</div>")
            
            # Прокрутка вниз
            self.chat_scroll.verticalScrollBar().setValue(
                self.chat_scroll.verticalScrollBar().maximum()
            )
    
    def delete_conversation(self):
        """Удаление выбранного разговора"""
        current_item = self.conversation_list.currentItem()
        if current_item:
            conv_index = current_item.data(Qt.ItemDataRole.UserRole)
            if 0 <= conv_index < len(self.conversations):
                self.conversations.pop(conv_index)
                self.save_conversations()
                self.update_conversation_list()
                self.new_conversation()
    
    def send_ai_query(self):
        """Отправка запроса ИИ"""
        query = self.ai_input.text().strip()
        if not query:
            return
        
        self.ai_input.clear()
        self.ask_ai(query)
    
    def ask_ai(self, query):
        """Запрос к ИИ"""
        # Показываем запрос пользователя
        self.chat_scroll.append(f"<div style='background-color: #e3f2fd; padding: 10px; border-radius: 8px; margin: 5px 0;'><b>You:</b> {query}</div>")
        self.current_conversation.append({
            'role': 'user',
            'content': query
        })
        
        # Показываем статус "думает"
        self.ai_status.setText("🤔 Thinking...")
        self.ai_status.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-weight: 600;
                padding: 6px 12px;
                background-color: #fff3cd;
                border-radius: 6px;
            }
        """)
        
        # Имитация задержки ИИ
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self.process_ai_response(query))
    
    def process_ai_response(self, query):
        """Обработка ответа ИИ"""
        try:
            # Получаем ответ от ИИ
            response = self.raven.process_command(query)
            
            # Отображаем ответ
            self.chat_scroll.append(f"<div style='background-color: #f8f9fa; padding: 10px; border-radius: 8px; margin: 5px 0;'><b>🤖 Raven AI:</b> {response}</div>")
            self.current_conversation.append({
                'role': 'assistant',
                'content': response
            })
            
            # Сохраняем разговор
            if len(self.current_conversation) >= 2:  # Минимум 2 сообщения
                conv_title = self.current_conversation[0]['content'][:50] + "..."
                self.conversations.append({
                    'title': conv_title,
                    'messages': self.current_conversation.copy()
                })
                self.save_conversations()
                self.update_conversation_list()
            
            # Возвращаем статус в норму
            self.ai_status.setText("✅ Ready")
            self.ai_status.setStyleSheet("""
                QLabel {
                    color: #2ecc71;
                    font-weight: 600;
                    padding: 6px 12px;
                    background-color: #e8f8f0;
                    border-radius: 6px;
                }
            """)
            
            # Прокрутка вниз
            self.chat_scroll.verticalScrollBar().setValue(
                self.chat_scroll.verticalScrollBar().maximum()
            )
            
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            self.chat_scroll.append(f"<div style='background-color: #ffeaea; padding: 10px; border-radius: 8px; margin: 5px 0; color: #e74c3c;'><b>⚠️ Error:</b> {error_msg}</div>")
            
            self.ai_status.setText("❌ Error")
            self.ai_status.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-weight: 600;
                    padding: 6px 12px;
                    background-color: #ffeaea;
                    border-radius: 6px;
                }
            """)
    
    def voice_query(self):
        """Голосовой запрос"""
        if not self.raven.is_voice_active:
            self.chat_scroll.append("<div style='background-color: #ffeaea; padding: 10px; border-radius: 8px; margin: 5px 0; color: #e74c3c;'><b>⚠️ Voice is disabled</b></div>")
            return
        
        import threading
        
        def listen():
            text = self.raven.listen(timeout=10)
            if text:
                self.ask_ai(text)
            else:
                self.chat_scroll.append("<div style='background-color: #ffeaea; padding: 10px; border-radius: 8px; margin: 5px 0; color: #e74c3c;'><b>⚠️ Could not recognize speech</b></div>")
        
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()