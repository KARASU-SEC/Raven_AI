"""
Современный интерфейс в стиле Jarvis/HUD
"""
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QGraphicsOpacityEffect,
                             QTextEdit, QLineEdit, QSlider, QProgressBar)
from PyQt6.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, 
                         QParallelAnimationGroup, pyqtProperty, QPoint, QRect)
from PyQt6.QtGui import (QFont, QColor, QPalette, QLinearGradient, QPainter,
                        QPainterPath, QBrush, QPen, QPixmap, QRadialGradient)
import qdarkstyle

class HolographicLabel(QLabel):
    """Голографический текст с эффектом свечения"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.glow_animation = QPropertyAnimation(self, b"glow")
        self.glow_animation.setDuration(2000)
        self.glow_animation.setLoopCount(-1)
        self.glow_animation.setStartValue(0.3)
        self.glow_animation.setEndValue(1.0)
        self.glow_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        
        self._glow_intensity = 0.5
        
    def getGlow(self):
        return self._glow_intensity
    
    def setGlow(self, value):
        self._glow_intensity = value
        self.update()
    
    glow = pyqtProperty(float, getGlow, setGlow)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Голографический эффект
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(0, 200, 255, int(255 * self._glow_intensity)))
        gradient.setColorAt(0.5, QColor(100, 255, 255, int(200 * self._glow_intensity)))
        gradient.setColorAt(1, QColor(0, 150, 255, int(255 * self._glow_intensity)))
        
        painter.setPen(QPen(gradient, 2))
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        
        # Эффект свечения
        painter.setPen(QPen(QColor(0, 255, 255, int(50 * self._glow_intensity)), 10))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
    
    def startAnimation(self):
        self.glow_animation.start()

class NeuralNetworkVisualizer(QWidget):
    """Визуализатор нейросетевой активности"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes = []
        self.connections = []
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_nodes)
        self.animation_timer.start(100)
        
    def update_nodes(self):
        import random
        if len(self.nodes) < 50:
            self.nodes.append({
                'x': random.randint(0, self.width()),
                'y': random.randint(0, self.height()),
                'size': random.randint(3, 8),
                'alpha': random.randint(50, 200),
                'speed': random.uniform(0.5, 2.0)
            })
        
        for node in self.nodes:
            node['x'] += random.uniform(-node['speed'], node['speed'])
            node['y'] += random.uniform(-node['speed'], node['speed'])
            node['alpha'] = (node['alpha'] + 5) % 255
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(10, 20, 40, 50))
        gradient.setColorAt(1, QColor(5, 10, 25, 100))
        painter.fillRect(self.rect(), gradient)
        
        # Соединения
        painter.setPen(QPen(QColor(0, 150, 255, 30), 1))
        for i, node1 in enumerate(self.nodes):
            for j, node2 in enumerate(self.nodes):
                if i < j and ((node1['x']-node2['x'])**2 + (node1['y']-node2['y'])**2)**0.5 < 100:
                    painter.drawLine(node1['x'], node1['y'], node2['x'], node2['y'])
        
        # Узлы
        for node in self.nodes:
            color = QColor(0, 200, 255, int(node['alpha']))
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(node['x'], node['y'], node['size'], node['size'])

class JarvisMainWindow(QMainWindow):
    """Главное окно в стиле Jarvis"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raven AI | Personal Assistant")
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # Центральный виджет с прозрачностью
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
        
        # Верхняя панель
        self.create_top_panel(main_layout)
        
        # Основное содержимое
        content_layout = QHBoxLayout()
        
        # Левая панель - HUD информация
        self.create_hud_panel(content_layout)
        
        # Центральная панель - Чат и управление
        self.create_central_panel(content_layout)
        
        # Правая панель - Системная информация
        self.create_system_panel(content_layout)
        
        main_layout.addLayout(content_layout)
        
        # Нижняя панель
        self.create_bottom_panel(main_layout)
        
        # Анимация появления
        self.animate_show()
        
        # Таймеры обновления
        self.setup_timers()
        
        # Стиль
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(5, 10, 30, 220),
                    stop:1 rgba(10, 20, 50, 200));
                border-radius: 20px;
                border: 2px solid rgba(0, 150, 255, 100);
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 100, 200, 150),
                    stop:1 rgba(0, 150, 255, 150));
                border: 1px solid rgba(0, 200, 255, 100);
                border-radius: 10px;
                padding: 10px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 120, 220, 200),
                    stop:1 rgba(50, 180, 255, 200));
            }
            
            QTextEdit {
                background-color: rgba(0, 10, 25, 150);
                border: 1px solid rgba(0, 100, 200, 100);
                border-radius: 10px;
                padding: 10px;
                color: #a0d2ff;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            
            QLineEdit {
                background-color: rgba(0, 20, 40, 200);
                border: 2px solid rgba(0, 150, 255, 150);
                border-radius: 10px;
                padding: 12px;
                color: white;
                font-size: 14px;
                selection-background-color: rgba(0, 150, 255, 100);
            }
            
            QLabel {
                color: #a0d2ff;
                font-weight: normal;
            }
            
            QProgressBar {
                border: 1px solid rgba(0, 150, 255, 100);
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 255, 200, 200),
                    stop:1 rgba(0, 150, 255, 200));
                border-radius: 5px;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid rgba(0, 150, 255, 100);
                height: 8px;
                background: rgba(0, 20, 40, 150);
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5,
                    stop:0 rgba(0, 200, 255, 255),
                    stop:1 rgba(0, 100, 200, 200));
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
        """)
    
    def create_top_panel(self, layout):
        """Создание верхней панели"""
        top_frame = QFrame()
        top_frame.setFixedHeight(80)
        top_layout = QHBoxLayout(top_frame)
        
        # Логотип и название
        logo = QLabel("🤖 RAVEN AI")
        logo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        logo.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 255, 255, 255),
                    stop:0.5 rgba(100, 255, 255, 255),
                    stop:1 rgba(0, 255, 255, 255));
                background: transparent;
            }
        """)
        
        # Статус системы
        self.status_hud = HolographicLabel("⚡ СИСТЕМА АКТИВНА")
        self.status_hud.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.status_hud.startAnimation()
        
        # Индикатор голоса
        self.voice_indicator = QLabel("🎤 ГОЛОСОВОЙ РЕЖИМ")
        self.voice_indicator.setStyleSheet("""
            QLabel {
                color: #00ffaa;
                font-weight: bold;
                padding: 5px 15px;
                background: rgba(0, 100, 100, 100);
                border-radius: 10px;
                border: 1px solid #00ffaa;
            }
        """)
        
        top_layout.addWidget(logo)
        top_layout.addStretch()
        top_layout.addWidget(self.status_hud)
        top_layout.addWidget(self.voice_indicator)
        
        layout.addWidget(top_frame)
    
    def create_hud_panel(self, layout):
        """Создание HUD панели"""
        hud_frame = QFrame()
        hud_frame.setFixedWidth(300)
        hud_layout = QVBoxLayout(hud_frame)
        
        # Визуализатор нейросети
        self.nn_visualizer = NeuralNetworkVisualizer()
        self.nn_visualizer.setFixedHeight(200)
        
        # Системные метрики
        metrics_frame = QFrame()
        metrics_layout = QVBoxLayout(metrics_frame)
        
        # CPU
        cpu_widget = self.create_metric_widget("💻 CPU", "45%", QColor(0, 200, 255))
        # RAM
        ram_widget = self.create_metric_widget("🧠 RAM", "68%", QColor(0, 255, 200))
        # Сеть
        net_widget = self.create_metric_widget("🌐 СЕТЬ", "12 Mbps", QColor(100, 200, 255))
        
        metrics_layout.addWidget(cpu_widget)
        metrics_layout.addWidget(ram_widget)
        metrics_layout.addWidget(net_widget)
        
        # Активные процессы
        processes_label = QLabel("📊 АКТИВНЫЕ ПРОЦЕССЫ")
        processes_label.setStyleSheet("color: #80d0ff; font-weight: bold; font-size: 14px;")
        
        self.processes_list = QTextEdit()
        self.processes_list.setReadOnly(True)
        self.processes_list.setMaximumHeight(150)
        
        hud_layout.addWidget(self.nn_visualizer)
        hud_layout.addWidget(metrics_frame)
        hud_layout.addWidget(processes_label)
        hud_layout.addWidget(self.processes_list)
        
        layout.addWidget(hud_frame)
    
    def create_central_panel(self, layout):
        """Создание центральной панели"""
        central_frame = QFrame()
        central_layout = QVBoxLayout(central_frame)
        
        # Чат с ассистентом
        chat_label = QLabel("💬 ДИАЛОГ С RAVEN")
        chat_label.setStyleSheet("""
            QLabel {
                color: #00ffcc;
                font-weight: bold;
                font-size: 16px;
                padding: 5px;
                background: rgba(0, 50, 100, 100);
                border-radius: 10px;
            }
        """)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(400)
        
        # Ввод сообщения
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение или нажмите 🎤 для голосового ввода...")
        
        self.voice_button = QPushButton("🎤")
        self.voice_button.setFixedSize(50, 50)
        self.voice_button.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.3, fy:0.3,
                    stop:0 rgba(0, 255, 200, 255),
                    stop:1 rgba(0, 150, 255, 200));
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.3, fy:0.3,
                    stop:0 rgba(100, 255, 255, 255),
                    stop:1 rgba(50, 200, 255, 200));
            }
        """)
        
        self.send_button = QPushButton("➤")
        self.send_button.setFixedSize(50, 50)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.voice_button)
        input_layout.addWidget(self.send_button)
        
        # Быстрые команды
        quick_cmds_label = QLabel("⚡ БЫСТРЫЕ КОМАНДЫ")
        quick_cmds_label.setStyleSheet("color: #80d0ff; font-weight: bold;")
        
        quick_buttons = QHBoxLayout()
        commands = ["📊 Система", "🌐 Интернет", "🎵 Музыка", "📁 Файлы", "🎮 Игры"]
        for cmd in commands:
            btn = QPushButton(cmd)
            btn.setMinimumHeight(40)
            quick_buttons.addWidget(btn)
        
        central_layout.addWidget(chat_label)
        central_layout.addWidget(self.chat_display)
        central_layout.addWidget(input_frame)
        central_layout.addWidget(quick_cmds_label)
        central_layout.addLayout(quick_buttons)
        
        layout.addWidget(central_frame, stretch=1)
    
    def create_system_panel(self, layout):
        """Создание правой панели системы"""
        system_frame = QFrame()
        system_frame.setFixedWidth(300)
        system_layout = QVBoxLayout(system_frame)
        
        # Активация
        activation_label = QLabel("🎯 АКТИВАЦИЯ")
        activation_label.setStyleSheet("""
            QLabel {
                color: #00ffaa;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        self.wake_word_label = QLabel("Ключевое слово: 'Raven'")
        self.wake_word_label.setStyleSheet("color: #a0f0ff;")
        
        self.activation_switch = QPushButton("🔘 ВКЛЮЧИТЬ АКТИВАЦИЮ")
        self.activation_switch.setCheckable(True)
        self.activation_switch.setChecked(True)
        
        # Настройки голоса
        voice_label = QLabel("🎙️ НАСТРОЙКИ ГОЛОСА")
        voice_label.setStyleSheet("""
            QLabel {
                color: #00ffaa;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        self.voice_combo = QLabel("Голос: Microsoft David (Премиум)")
        self.voice_combo.setStyleSheet("color: #a0f0ff;")
        
        speed_label = QLabel("Скорость:")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 300)
        self.speed_slider.setValue(180)
        
        volume_label = QLabel("Громкость:")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(90)
        
        # AI настройки
        ai_label = QLabel("🧠 AI НАСТРОЙКИ")
        ai_label.setStyleSheet("""
            QLabel {
                color: #00ffaa;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        self.ai_model_label = QLabel("Модель: NeuralNet v2.1")
        self.ai_model_label.setStyleSheet("color: #a0f0ff;")
        
        self.ai_status = QProgressBar()
        self.ai_status.setValue(75)
        self.ai_status.setFormat("Загрузка AI: %p%")
        
        system_layout.addWidget(activation_label)
        system_layout.addWidget(self.wake_word_label)
        system_layout.addWidget(self.activation_switch)
        system_layout.addSpacing(20)
        system_layout.addWidget(voice_label)
        system_layout.addWidget(self.voice_combo)
        system_layout.addWidget(speed_label)
        system_layout.addWidget(self.speed_slider)
        system_layout.addWidget(volume_label)
        system_layout.addWidget(self.volume_slider)
        system_layout.addSpacing(20)
        system_layout.addWidget(ai_label)
        system_layout.addWidget(self.ai_model_label)
        system_layout.addWidget(self.ai_status)
        
        layout.addWidget(system_frame)
    
    def create_bottom_panel(self, layout):
        """Создание нижней панели"""
        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout(bottom_frame)
        
        # Время и дата
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #00ffff;")
        
        # Статусная строка
        self.status_bar = QLabel("✅ Система готова к работе | Версия 2.0 | Нейросеть активна")
        self.status_bar.setStyleSheet("color: #80d0ff;")
        
        # Кнопки управления окном
        minimize_btn = QPushButton("─")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        
        bottom_layout.addWidget(self.time_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.status_bar)
        bottom_layout.addStretch()
        bottom_layout.addWidget(minimize_btn)
        bottom_layout.addWidget(close_btn)
        
        layout.addWidget(bottom_frame)
    
    def create_metric_widget(self, title, value, color):
        """Создание виджета метрики"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: rgba({color.red()}, {color.green()}, {color.blue()}, 30);
                border: 1px solid rgba({color.red()}, {color.green()}, {color.blue()}, 100);
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: rgb({color.red()}, {color.green()}, {color.blue()}); font-weight: bold;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return widget
    
    def animate_show(self):
        """Анимация появления окна"""
        self.setWindowOpacity(0)
        
        self.show()
        
        animation = QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(500)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
    
    def setup_timers(self):
        """Настройка таймеров обновления"""
        # Таймер времени
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()
        
        # Таймер системной информации
        self.sys_timer = QTimer()
        self.sys_timer.timeout.connect(self.update_system_info)
        self.sys_timer.start(2000)
    
    def update_time(self):
        """Обновление времени"""
        from datetime import datetime
        now = datetime.now()
        self.time_label.setText(now.strftime("🕒 %H:%M:%S | 📅 %d.%m.%Y"))
    
    def update_system_info(self):
        """Обновление системной информации"""
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent()
            
            # RAM
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            
            # Обновляем метрики
            # Здесь будет код обновления виджетов
            
            # Процессы
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    info = proc.info
                    if info['cpu_percent'] > 1.0:
                        processes.append(f"{info['name'][:20]}: {info['cpu_percent']:.1f}%")
                        if len(processes) >= 8:
                            break
                except:
                    pass
            
            self.processes_list.setText("\n".join(processes) if processes else "Нет активных процессов")
            
        except Exception as e:
            print(f"Ошибка обновления системной информации: {e}")
    
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