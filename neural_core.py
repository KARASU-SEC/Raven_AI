"""
Ядро искусственного интеллекта Raven AI (исправленная версия)
"""
import numpy as np
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
import hashlib

# ИСПРАВЛЕНО: Убираем зависимость от torch если не установлен
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch не установлен. Используется упрощенный режим.")

class NeuralCore:
    """Нейросетевое ядро для понимания и генерации ответов"""
    
    def __init__(self, model_path: str = "models/neural_core.pt"):
        self.model_path = model_path
        
        # Контекстная память
        self.context_memory = []
        self.max_context = 10
        
        # Навыки
        self.skills = self.load_skills()
        
        # Загрузка модели если torch доступен
        if TORCH_AVAILABLE:
            self.setup_neural_network()
            self.load_model()
        else:
            print("🧠 Neural Core в упрощенном режиме (без PyTorch)")
    
    def setup_neural_network(self):
        """Настройка нейросети (только если torch доступен)"""
        if not TORCH_AVAILABLE:
            return
            
        class SimpleNeuralNetwork(nn.Module):
            def __init__(self):
                super().__init__()
                self.embedding = nn.Embedding(1000, 128)
                self.fc1 = nn.Linear(128, 256)
                self.fc2 = nn.Linear(256, 128)
                self.fc3 = nn.Linear(128, 1000)
                self.dropout = nn.Dropout(0.3)
                self.relu = nn.ReLU()
            
            def forward(self, x):
                embedded = self.embedding(x)
                x = self.relu(self.fc1(embedded.mean(dim=1)))
                x = self.dropout(x)
                x = self.relu(self.fc2(x))
                x = self.dropout(x)
                x = self.fc3(x)
                return x
        
        self.model = SimpleNeuralNetwork()
        self.vocab = {}
        self.inv_vocab = {}
    
    def process_query(self, query: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """Обработка запроса пользователя"""
        # Анализ намерения
        intent = self.detect_intent(query)
        
        # Извлечение сущностей
        entities = self.extract_entities(query)
        
        # Определение навыка
        skill = self.select_skill(intent, entities)
        
        # Генерация ответа
        if skill:
            response = self.execute_skill(skill, query, entities)
        else:
            response = self.generate_response(query, context)
        
        # Обновление контекста
        self.update_context(query, response)
        
        # Анализ эмоций
        emotion = self.analyze_emotion(query)
        
        return {
            'query': query,
            'intent': intent,
            'entities': entities,
            'skill': skill,
            'response': response,
            'emotion': emotion,
            'timestamp': datetime.now().isoformat(),
            'context_id': self.generate_context_id(query)
        }
    
    def detect_intent(self, query: str) -> str:
        """Определение намерения пользователя"""
        query_lower = query.lower()
        
        # Интент-детекция
        intents = {
            'greeting': ['привет', 'здравствуй', 'добрый', 'хай', 'hello', 'hi'],
            'farewell': ['пока', 'до свидания', 'прощай', 'bye', 'goodbye'],
            'question': ['как', 'почему', 'что', 'где', 'когда', 'кто', 'какой'],
            'command': ['открой', 'закрой', 'запусти', 'выключи', 'покажи', 'найди'],
            'system': ['система', 'процессы', 'память', 'cpu', 'ram', 'диск'],
            'time': ['время', 'который час', 'дата', 'число'],
            'weather': ['погода', 'температура', 'дождь', 'солнце'],
            'entertainment': ['музыка', 'фильм', 'игра', 'развлечение', 'шутка']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        
        return 'unknown'
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Извлечение сущностей из запроса"""
        entities = {
            'applications': [],
            'files': [],
            'urls': [],
            'numbers': [],
            'dates': [],
            'times': [],
            'locations': []
        }
        
        # Простая реализация извлечения сущностей
        words = query.lower().split()
        
        # Приложения
        apps = ['браузер', 'chrome', 'firefox', 'edge', 'notepad', 'блокнот', 
                'калькулятор', 'word', 'excel', 'steam', 'discord']
        entities['applications'] = [word for word in words if word in apps]
        
        # Числа
        import re
        numbers = re.findall(r'\d+', query)
        entities['numbers'] = [int(num) for num in numbers]
        
        # Время
        time_patterns = [r'\d{1,2}:\d{2}', r'\d{1,2} часов', r'\d{1,2} час']
        for pattern in time_patterns:
            times = re.findall(pattern, query)
            entities['times'].extend(times)
        
        return entities
    
    def select_skill(self, intent: str, entities: Dict) -> Optional[str]:
        """Выбор навыка для обработки запроса"""
        skill_map = {
            'greeting': 'conversation',
            'farewell': 'conversation',
            'question': 'knowledge',
            'command': 'system_control',
            'system': 'system_monitor',
            'time': 'datetime',
            'weather': 'weather',
            'entertainment': 'entertainment'
        }
        
        # Проверка на системные команды
        if entities.get('applications'):
            return 'application_control'
        
        return skill_map.get(intent, 'general')
    
    def execute_skill(self, skill: str, query: str, entities: Dict) -> str:
        """Выполнение навыка"""
        skill_handlers = {
            'conversation': self.handle_conversation,
            'system_control': self.handle_system_control,
            'system_monitor': self.handle_system_monitor,
            'application_control': self.handle_application_control,
            'datetime': self.handle_datetime,
            'knowledge': self.handle_knowledge,
            'general': self.handle_general
        }
        
        handler = skill_handlers.get(skill, self.handle_general)
        return handler(query, entities)
    
    def handle_conversation(self, query: str, entities: Dict) -> str:
        """Обработка разговорных запросов"""
        responses = {
            'greeting': [
                "Привет! Рад вас слышать. Чем могу помочь?",
                "Здравствуйте! Raven AI к вашим услугам.",
                "Приветствую! Готов выполнить ваши команды."
            ],
            'farewell': [
                "До свидания! Буду ждать вашего возвращения.",
                "Всего хорошего! Не стесняйтесь обращаться.",
                "Прощайте! Надеюсь, я был полезен."
            ],
            'thanks': [
                "Всегда рад помочь!",
                "Пожалуйста! Обращайтесь ещё.",
                "Не за что! Это моя работа."
            ]
        }
        
        import random
        intent = self.detect_intent(query)
        
        if 'спасибо' in query.lower():
            return random.choice(responses['thanks'])
        
        return random.choice(responses.get(intent, ["Я вас слушаю."]))
    
    def handle_system_control(self, query: str, entities: Dict) -> str:
        """Управление системой"""
        import psutil
        import subprocess
        
        query_lower = query.lower()
        
        if 'открой' in query_lower or 'запусти' in query_lower:
            if entities.get('applications'):
                app = entities['applications'][0]
                try:
                    # Маппинг приложений
                    app_map = {
                        'браузер': 'chrome.exe',
                        'chrome': 'chrome.exe',
                        'блокнот': 'notepad.exe',
                        'notepad': 'notepad.exe',
                        'калькулятор': 'calc.exe',
                        'calc': 'calc.exe'
                    }
                    
                    app_exe = app_map.get(app, app + '.exe')
                    subprocess.Popen(app_exe, shell=True)
                    return f"✅ Запускаю {app}"
                except Exception as e:
                    return f"❌ Не удалось запустить {app}: {str(e)}"
        
        elif 'закрой' in query_lower:
            # Закрытие приложений
            for proc in psutil.process_iter(['name']):
                try:
                    if any(app in proc.info['name'].lower() for app in entities.get('applications', [])):
                        proc.terminate()
                        return f"✅ Закрыл {proc.info['name']}"
                except:
                    pass
            return "⚠️ Не удалось найти указанное приложение"
        
        elif 'выключи' in query_lower and ('компьютер' in query_lower or 'пк' in query_lower):
            return "⚠️ Команда выключения компьютера требует подтверждения"
        
        return "ℹ️ Системная команда обработана"
    
    def handle_system_monitor(self, query: str, entities: Dict) -> str:
        """Мониторинг системы"""
        import psutil
        
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('C:/').percent if os.name == 'nt' else psutil.disk_usage('/').percent
        
        return f"📊 Состояние системы: CPU {cpu}%, RAM {ram}%, Диск {disk}%"
    
    def handle_application_control(self, query: str, entities: Dict) -> str:
        """Управление приложениями"""
        return self.handle_system_control(query, entities)
    
    def handle_datetime(self, query: str, entities: Dict) -> str:
        """Информация о времени и дате"""
        from datetime import datetime
        
        now = datetime.now()
        
        if 'время' in query.lower():
            return f"🕒 Сейчас {now.strftime('%H:%M:%S')}"
        elif 'дата' in query.lower():
            return f"📅 Сегодня {now.strftime('%d.%m.%Y')}"
        else:
            return f"🕒 {now.strftime('%H:%M:%S')} 📅 {now.strftime('%d.%m.%Y')}"
    
    def handle_knowledge(self, query: str, entities: Dict) -> str:
        """Ответы на вопросы"""
        # Простая база знаний
        knowledge_base = {
            'кто ты': 'Я Raven AI, ваш персональный голосовой ассистент.',
            'что ты умеешь': 'Я могу управлять системой, отвечать на вопросы, открывать приложения и многое другое.',
            'создатель': 'Меня создали как проект с открытым исходным кодом.',
            'версия': 'Текущая версия: Raven AI 2.1 Dashboard Edition'
        }
        
        for pattern, answer in knowledge_base.items():
            if pattern in query.lower():
                return answer
        
        # Если вопрос не найден
        return "🤔 Интересный вопрос. Позвольте мне подумать..."
    
    def handle_general(self, query: str, entities: Dict) -> str:
        """Обработка общих запросов"""
        return "Я понял ваш запрос. Уточните, пожалуйста, что именно вы хотите сделать?"
    
    def generate_response(self, query: str, context: Optional[List[str]] = None) -> str:
        """Генерация ответа"""
        return self.handle_general(query, {})
    
    def analyze_emotion(self, query: str) -> str:
        """Анализ эмоциональной окраски запроса"""
        positive_words = ['хорошо', 'отлично', 'спасибо', 'класс', 'супер', 'люблю']
        negative_words = ['плохо', 'ужасно', 'ненавижу', 'бесит', 'раздражает']
        
        query_lower = query.lower()
        
        pos_count = sum(1 for word in positive_words if word in query_lower)
        neg_count = sum(1 for word in negative_words if word in query_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def update_context(self, query: str, response: str):
        """Обновление контекстной памяти"""
        self.context_memory.append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        if len(self.context_memory) > self.max_context:
            self.context_memory.pop(0)
    
    def generate_context_id(self, query: str) -> str:
        """Генерация ID контекста"""
        return hashlib.md5(query.encode()).hexdigest()[:8]
    
    def load_skills(self) -> Dict:
        """Загрузка навыков из файла"""
        try:
            skills_path = 'config/skills.json'
            if os.path.exists(skills_path):
                with open(skills_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_model(self):
        """Сохранение модели"""
        if TORCH_AVAILABLE:
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'vocab': self.vocab,
                'inv_vocab': self.inv_vocab
            }, self.model_path)
    
    def load_model(self):
        """Загрузка модели"""
        if not TORCH_AVAILABLE:
            return
            
        try:
            if os.path.exists(self.model_path):
                checkpoint = torch.load(self.model_path)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.vocab = checkpoint['vocab']
                self.inv_vocab = checkpoint['inv_vocab']
                print("✅ Модель нейросети загружена")
        except Exception as e:
            print(f"⚠️ Не удалось загрузить модель: {e}")