"""
Страница мониторинга системы
"""
import os
import psutil
import platform
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGroupBox, QTableWidget,
                             QTableWidgetItem, QProgressBar, QTabWidget,
                             QTreeWidget, QTreeWidgetItem, QSplitter)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QBrush

class SystemPage(QWidget):
    """Страница мониторинга системы"""
    
    def __init__(self, raven_ai):
        super().__init__()
        self.raven = raven_ai
        self.setup_ui()
        self.setup_timers()
    
    def setup_ui(self):
        """Настройка интерфейса страницы"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel("⚙️ System Monitor")
        title.setStyleSheet("""
            color: #2c3e50;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Вкладки
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
        
        # Вкладка 1: Обзор системы
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        overview_layout.addWidget(self.create_overview_widget())
        tabs.addTab(overview_tab, "Overview")
        
        # Вкладка 2: Процессы
        processes_tab = QWidget()
        processes_layout = QVBoxLayout(processes_tab)
        processes_layout.addWidget(self.create_processes_widget())
        tabs.addTab(processes_tab, "Processes")
        
        # Вкладка 3: Сеть
        network_tab = QWidget()
        network_layout = QVBoxLayout(network_tab)
        network_layout.addWidget(self.create_network_widget())
        tabs.addTab(network_tab, "Network")
        
        # Вкладка 4: Диск
        disk_tab = QWidget()
        disk_layout = QVBoxLayout(disk_tab)
        disk_layout.addWidget(self.create_disk_widget())
        tabs.addTab(disk_tab, "Disk")
        
        layout.addWidget(tabs)
    
    def create_overview_widget(self):
        """Создание виджета обзора системы"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Информация о системе
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout()
        
        self.system_info = QLabel()
        self.system_info.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', monospace;
                font-size: 13px;
                color: #2c3e50;
            }
        """)
        info_layout.addWidget(self.system_info)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Графики использования
        usage_group = QGroupBox("Resource Usage")
        usage_layout = QVBoxLayout()
        
        # CPU
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU:")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        self.cpu_percent = QLabel("0%")
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_progress)
        cpu_layout.addWidget(self.cpu_percent)
        usage_layout.addLayout(cpu_layout)
        
        # RAM
        ram_layout = QHBoxLayout()
        ram_label = QLabel("RAM:")
        self.ram_progress = QProgressBar()
        self.ram_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 3px;
            }
        """)
        self.ram_percent = QLabel("0%")
        ram_layout.addWidget(ram_label)
        ram_layout.addWidget(self.ram_progress)
        ram_layout.addWidget(self.ram_percent)
        usage_layout.addLayout(ram_layout)
        
        # Disk
        disk_layout = QHBoxLayout()
        disk_label = QLabel("Disk:")
        self.disk_progress = QProgressBar()
        self.disk_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #9b59b6;
                border-radius: 3px;
            }
        """)
        self.disk_percent = QLabel("0%")
        disk_layout.addWidget(disk_label)
        disk_layout.addWidget(self.disk_progress)
        disk_layout.addWidget(self.disk_percent)
        usage_layout.addLayout(disk_layout)
        
        usage_group.setLayout(usage_layout)
        layout.addWidget(usage_group)
        
        # Быстрые действия
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.update_system_info)
        
        kill_btn = QPushButton("Kill Process")
        kill_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        kill_btn.clicked.connect(self.kill_selected_process)
        
        cleanup_btn = QPushButton("🧹 Cleanup")
        cleanup_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
        """)
        cleanup_btn.clicked.connect(self.perform_cleanup)
        
        actions_layout.addWidget(refresh_btn)
        actions_layout.addWidget(kill_btn)
        actions_layout.addWidget(cleanup_btn)
        actions_layout.addStretch()
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        return widget
    
    def create_processes_widget(self):
        """Создание виджета процессов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Таблица процессов
        self.processes_table = QTableWidget()
        self.processes_table.setColumnCount(5)
        self.processes_table.setHorizontalHeaderLabels(["PID", "Name", "CPU %", "Memory %", "Status"])
        self.processes_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-right: 1px solid #e0e0e0;
                font-weight: 600;
            }
        """)
        
        layout.addWidget(self.processes_table)
        return widget
    
    def create_network_widget(self):
        """Создание виджета сети"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.network_info = QLabel("Network information will be displayed here")
        self.network_info.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', monospace;
                font-size: 13px;
                color: #2c3e50;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
        """)
        self.network_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.network_info)
        return widget
    
    def create_disk_widget(self):
        """Создание виджета диска"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.disk_info = QLabel("Disk information will be displayed here")
        self.disk_info.setStyleSheet("""
            QLabel {
                font-family: 'Consolas', monospace;
                font-size: 13px;
                color: #2c3e50;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
        """)
        self.disk_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.disk_info)
        return widget
    
    def setup_timers(self):
        """Настройка таймеров обновления"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_system_info)
        self.update_timer.start(2000)
        
        self.update_system_info()
    
    def update_system_info(self):
        """Обновление информации о системе"""
        # Общая информация
        sys_info = f"""
Operating System: {platform.system()} {platform.release()}
Processor: {platform.processor()}
Architecture: {platform.architecture()[0]}
Python Version: {platform.python_version()}
        
Boot Time: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}
Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        self.system_info.setText(sys_info.strip())
        
        # Использование ресурсов
        cpu_percent = psutil.cpu_percent()
        self.cpu_progress.setValue(int(cpu_percent))
        self.cpu_percent.setText(f"{cpu_percent:.1f}%")
        
        ram = psutil.virtual_memory()
        self.ram_progress.setValue(int(ram.percent))
        self.ram_percent.setText(f"{ram.percent:.1f}%")
        
        disk = psutil.disk_usage('C:/' if os.name == 'nt' else '/')
        self.disk_progress.setValue(int(disk.percent))
        self.disk_percent.setText(f"{disk.percent:.1f}%")
        
        # Обновление таблицы процессов
        self.update_processes_table()
        
        # Обновление информации о сети
        self.update_network_info()
        
        # Обновление информации о диске
        self.update_disk_info()
    
    def update_processes_table(self):
        """Обновление таблицы процессов"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                processes.append(proc.info)
            
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            self.processes_table.setRowCount(min(50, len(processes)))
            
            for i, proc in enumerate(processes[:50]):
                # PID
                pid_item = QTableWidgetItem(str(proc['pid']))
                pid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.processes_table.setItem(i, 0, pid_item)
                
                # Имя
                name_item = QTableWidgetItem(proc['name'][:30])
                self.processes_table.setItem(i, 1, name_item)
                
                # CPU
                cpu_item = QTableWidgetItem(f"{proc['cpu_percent'] or 0:.1f}%")
                cpu_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                cpu_value = proc['cpu_percent'] or 0
                if cpu_value > 70:
                    cpu_item.setForeground(QBrush(QColor('#e74c3c')))
                elif cpu_value > 30:
                    cpu_item.setForeground(QBrush(QColor('#f39c12')))
                else:
                    cpu_item.setForeground(QBrush(QColor('#27ae60')))
                
                self.processes_table.setItem(i, 2, cpu_item)
                
                # Memory
                mem_item = QTableWidgetItem(f"{proc['memory_percent'] or 0:.1f}%")
                mem_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.processes_table.setItem(i, 3, mem_item)
                
                # Status
                status_item = QTableWidgetItem(proc['status'])
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.processes_table.setItem(i, 4, status_item)
            
            self.processes_table.resizeColumnsToContents()
        except Exception as e:
            print(f"Process table update error: {e}")
    
    def update_network_info(self):
        """Обновление информации о сети"""
        try:
            net_io = psutil.net_io_counters()
            info = f"""
Network Statistics:
Bytes Sent: {net_io.bytes_sent:,}
Bytes Received: {net_io.bytes_recv:,}
Packets Sent: {net_io.packets_sent:,}
Packets Received: {net_io.packets_recv:,}
            """
            self.network_info.setText(info.strip())
        except:
            self.network_info.setText("Network information not available")
    
    def update_disk_info(self):
        """Обновление информации о диске"""
        try:
            disk_usage = psutil.disk_usage('/')
            info = f"""
Disk Usage (C:/):
Total: {disk_usage.total / (1024**3):.1f} GB
Used: {disk_usage.used / (1024**3):.1f} GB ({disk_usage.percent}%)
Free: {disk_usage.free / (1024**3):.1f} GB
            """
            self.disk_info.setText(info.strip())
        except:
            self.disk_info.setText("Disk information not available")
    
    def kill_selected_process(self):
        """Завершить выбранный процесс"""
        current_row = self.processes_table.currentRow()
        if current_row >= 0:
            pid_item = self.processes_table.item(current_row, 0)
            if pid_item:
                try:
                    pid = int(pid_item.text())
                    psutil.Process(pid).terminate()
                    self.raven.speak(f"Process {pid} terminated")
                except Exception as e:
                    self.raven.speak(f"Error terminating process: {str(e)}")
    
    def perform_cleanup(self):
        """Выполнить очистку системы"""
        import gc
        gc.collect()
        self.raven.speak("System cleanup performed")
    
    def cleanup(self):
        """Очистка ресурсов"""
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()