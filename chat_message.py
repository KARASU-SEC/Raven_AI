"""
Компонент сообщения в чате
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class ChatMessage(QFrame):
    """Сообщение в чате"""
    
    def __init__(self, text, is_user=False, time=""):
        super().__init__()
        self.setup_ui(text, is_user, time)
    
    def setup_ui(self, text, is_user, time):
        """Настройка интерфейса сообщения"""
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                margin: 5px 0;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        
        # Сообщение
        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setMaximumWidth(400)
        
        if is_user:
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #3498db;
                    color: white;
                    border-radius: 18px;
                    padding: 12px 16px;
                    font-size: 14px;
                    margin-left: 50px;
                }
            """)
            layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    border-radius: 18px;
                    padding: 12px 16px;
                    font-size: 14px;
                    border: 1px solid #e0e0e0;
                    margin-right: 50px;
                }
            """)
            layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        layout.addWidget(message_label)
        
        # Время
        if time:
            time_label = QLabel(time)
            time_label.setStyleSheet("""
                color: #95a5a6;
                font-size: 11px;
            """)
            if is_user:
                time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            else:
                time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(time_label)