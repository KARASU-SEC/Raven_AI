"""
API endpoints для AI Assistant
"""
import json
import time
from datetime import datetime
from flask import jsonify, request
import threading
import queue

class AIAPI:
    """API для работы с искусственным интеллектом"""
    
    def __init__(self, raven_ai):
        self.raven = raven_ai
        self.chat_history = []
        self.thinking_queue = queue.Queue()
        self.setup_ai_threads()
    
    def setup_ai_threads(self):
        """Настройка потоков для обработки AI запросов"""
        self.is_processing = True
        self.ai_thread = threading.Thread(target=self.process_ai_queue, daemon=True)
        self.ai_thread.start()
    
    def process_ai_queue(self):
        """Обработка очереди AI запросов"""
        while self.is_processing:
            try:
                task = self.thinking_queue.get(timeout=0.5)
                if task:
                    task_id, message, callback = task
                    try:
                        # Обработка сообщения через ИИ
                        response = self.process_ai_message(message)
                        callback(task_id, response, True)
                    except Exception as e:
                        callback(task_id, str(e), False)
            except queue.Empty:
                continue
    
    def process_ai_message(self, message):
        """Обработка сообщения через ИИ"""
        # Используем существующий raven_ai для обработки
        if hasattr(self.raven, 'process_command'):
            return self.raven.process_command(message)
        
        # Fallback обработка
        return self.fallback_ai_response(message)
    
    def fallback_ai_response(self, message):
        """Резервный метод обработки AI"""
        message_lower = message.lower()
        
        # Простые правила для демонстрации
        if any(word in message_lower for word in ['привет', 'здравствуй', 'hello', 'hi']):
            return "Привет! Я Raven AI. Как я могу помочь вам сегодня?"
        
        elif any(word in message_lower for word in ['время', 'который час']):
            return f"Сейчас {datetime.now().strftime('%H:%M:%S')}"
        
        elif any(word in message_lower for word in ['дата', 'число', 'день']):
            return f"Сегодня {datetime.now().strftime('%d.%m.%Y')}"
        
        elif any(word in message_lower for word in ['система', 'cpu', 'ram', 'память']):
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            return f"Системная информация: CPU {cpu}%, RAM {ram}%"
        
        elif 'погода' in message_lower:
            return "К сожалению, у меня нет доступа к данным о погоде в этой версии."
        
        elif any(word in message_lower for word in ['помощь', 'help', 'команды']):
            return """Я могу помочь с:
1. Ответами на вопросы
2. Информацией о системе
3. Основными вычислениями
4. Общими знаниями
Что вас интересует?"""
        
        else:
            return f"Я получил ваше сообщение: '{message}'. В полной версии я буду использовать продвинутые нейросетевые модели для более точных ответов."
    
    def register_endpoints(self, app):
        """Регистрация endpoints API"""
        
        @app.route('/api/ai/chat', methods=['POST'])
        def ai_chat():
            """Основной endpoint для чата с AI"""
            try:
                data = request.json
                message = data.get('message', '')
                model = data.get('model', 'neural_core')
                settings = data.get('settings', {})
                context = data.get('context', [])
                
                if not message:
                    return jsonify({
                        'success': False,
                        'error': 'No message provided'
                    }), 400
                
                # Обработка сообщения
                response = self.process_ai_message(message)
                
                # Сохраняем в историю
                chat_entry = {
                    'user': message,
                    'ai': response,
                    'model': model,
                    'settings': settings,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.chat_history.append(chat_entry)
                
                # Ограничиваем историю
                if len(self.chat_history) > 100:
                    self.chat_history = self.chat_history[-100:]
                
                return jsonify({
                    'success': True,
                    'response': response,
                    'model': model,
                    'timestamp': datetime.now().isoformat(),
                    'history_length': len(self.chat_history)
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @app.route('/api/ai/models', methods=['GET'])
        def get_ai_models():
            """Получение списка доступных AI моделей"""
            models = [
                {
                    'id': 'neural_core',
                    'name': 'Neural Core v2.1',
                    'description': 'Локальная нейросеть с памятью контекста',
                    'type': 'local',
                    'tokens': 1200,
                    'context_size': 10,
                    'accuracy': 0.87,
                    'speed_ms': 42
                },
                {
                    'id': 'raven_ai',
                    'name': 'Raven AI Core',
                    'description': 'Основной движок Raven AI',
                    'type': 'local',
                    'tokens': 800,
                    'context_size': 5,
                    'accuracy': 0.92,
                    'speed_ms': 28
                },
                {
                    'id': 'openai',
                    'name': 'OpenAI GPT-3.5',
                    'description': 'Облачная модель OpenAI',
                    'type': 'cloud',
                    'tokens': 4000,
                    'context_size': 16,
                    'accuracy': 0.95,
                    'speed_ms': 1200
                },
                {
                    'id': 'local_llm',
                    'name': 'Local LLM',
                    'description': 'Локальная большая языковая модель',
                    'type': 'local',
                    'tokens': 2500,
                    'context_size': 8,
                    'accuracy': 0.78,
                    'speed_ms': 850
                }
            ]
            
            return jsonify({
                'success': True,
                'models': models,
                'default_model': 'neural_core'
            })
        
        @app.route('/api/ai/history', methods=['GET', 'DELETE'])
        def ai_history():
            """Управление историей чата"""
            if request.method == 'GET':
                limit = request.args.get('limit', default=50, type=int)
                history = self.chat_history[-limit:] if limit > 0 else self.chat_history
                
                return jsonify({
                    'success': True,
                    'history': history,
                    'total': len(self.chat_history)
                })
            
            elif request.method == 'DELETE':
                self.chat_history = []
                return jsonify({
                    'success': True,
                    'message': 'Chat history cleared'
                })
        
        @app.route('/api/ai/status', methods=['GET'])
        def ai_status():
            """Статус AI системы"""
            import psutil
            
            # Получаем использование памяти
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return jsonify({
                'success': True,
                'status': 'active',
                'models_loaded': 2,
                'memory_usage_mb': memory_info.rss / (1024 * 1024),
                'chat_history_count': len(self.chat_history),
                'queue_size': self.thinking_queue.qsize(),
                'timestamp': datetime.now().isoformat()
            })
        
        @app.route('/api/ai/analyze', methods=['POST'])
        def ai_analyze():
            """Анализ текста"""
            try:
                data = request.json
                text = data.get('text', '')
                
                if not text:
                    return jsonify({'error': 'No text provided'}), 400
                
                # Простой анализ текста
                word_count = len(text.split())
                char_count = len(text)
                sentence_count = text.count('.') + text.count('!') + text.count('?')
                
                # Определение тональности (очень упрощённо)
                positive_words = ['хорошо', 'отлично', 'прекрасно', 'спасибо', 'люблю']
                negative_words = ['плохо', 'ужасно', 'ненавижу', 'разочарован']
                
                positive_count = sum(1 for word in positive_words if word in text.lower())
                negative_count = sum(1 for word in negative_words if word in text.lower())
                
                sentiment = 'neutral'
                if positive_count > negative_count:
                    sentiment = 'positive'
                elif negative_count > positive_count:
                    sentiment = 'negative'
                
                return jsonify({
                    'success': True,
                    'analysis': {
                        'word_count': word_count,
                        'character_count': char_count,
                        'sentence_count': sentence_count,
                        'reading_time_minutes': round(word_count / 200, 1),  # 200 слов в минуту
                        'sentiment': sentiment,
                        'positive_words': positive_count,
                        'negative_words': negative_count
                    },
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/ai/summarize', methods=['POST'])
        def ai_summarize():
            """Суммаризация текста"""
            try:
                data = request.json
                text = data.get('text', '')
                
                if not text:
                    return jsonify({'error': 'No text provided'}), 400
                
                # Упрощённая суммаризация
                sentences = text.split('.')
                if len(sentences) > 3:
                    summary = '. '.join(sentences[:3]) + '.'
                else:
                    summary = text
                
                return jsonify({
                    'success': True,
                    'original_length': len(text),
                    'summary_length': len(summary),
                    'reduction_percent': round((1 - len(summary) / len(text)) * 100, 1),
                    'summary': summary,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/ai/translate', methods=['POST'])
        def ai_translate():
            """Перевод текста"""
            try:
                data = request.json
                text = data.get('text', '')
                target_lang = data.get('target_lang', 'en')
                
                if not text:
                    return jsonify({'error': 'No text provided'}), 400
                
                # Упрощённый перевод (для демонстрации)
                translations = {
                    'привет': 'hello',
                    'пока': 'goodbye',
                    'спасибо': 'thank you',
                    'пожалуйста': 'you\'re welcome'
                }
                
                words = text.lower().split()
                translated_words = []
                
                for word in words:
                    if word in translations:
                        translated_words.append(translations[word])
                    else:
                        translated_words.append(word)
                
                translation = ' '.join(translated_words)
                
                return jsonify({
                    'success': True,
                    'original': text,
                    'translation': translation,
                    'target_language': target_lang,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500