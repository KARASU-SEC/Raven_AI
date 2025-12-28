"""
Компонент карточки с метрикой
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class MetricCard(QFrame):
    """Карточка с метрикой для дашборда"""
    
    def __init__(self, title, value, icon="", trend="", color="#3498db"):
        super().__init__()
        self.color = color
        self.setup_ui(title, value, icon, trend)
    
    def setup_ui(self, title, value, icon, trend):
        """Настройка интерфейса карточки"""
        self.setFixedHeight(120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
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
        self.value_label.setStyleSheet(f"""
            color: {self.color};
            font-size: 32px;
            font-weight: 700;
            margin: 5px 0;
        """)
        layout.addWidget(self.value_label)
        
        # Тренд
        if trend:
            trend_label = QLabel(trend)
            trend_color = "#2ecc71" if trend.startswith("+") else "#e74c3c"
            trend_label.setStyleSheet(f"""
                color: {trend_color};
                font-size: 12px;
                font-weight: 600;
                padding: 2px 8px;
                background-color: {trend_color}15;
                border-radius: 4px;
            """)
            layout.addWidget(trend_label)
        
        layout.addStretch()
    
    def set_value(self, value):
        """Установка значения"""
        self.value_label.setText(value)