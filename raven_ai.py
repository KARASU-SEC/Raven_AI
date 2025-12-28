"""
Ядро Raven AI с ИИ и голосовыми функциями
"""
import speech_recognition as sr
import pyttsx3
import psutil
import webbrowser
import subprocess
import platform
from datetime import datetime
import threading
import json
import os
import time

class RavenAI:
    """Ядро ИИ ассистента"""
    
    def __init__(self):
        print("🧠 Инициализация Raven AI...")
        
        # Инициализация голосового движка
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Инициализация распознавания речи
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Состояние системы
        self.is_voice_active = True
        self.is_listening = False
        
        # История команд
        self.command_history = []
        
        # Загрузка навыков
        self.skills = self.load_skills()
        
        print("✅ Raven AI готов к работе")
    
    def setup_tts(self):
        """Настройка синтеза речи"""
        try:
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'russian' in voice.name.lower() or 'ru' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            self.tts_engine.setProperty('rate', 170)
            self.tts_engine.setProperty('volume', 0.9)
            print("✅ TTS настроен")
        except Exception as e:
            print(f"⚠️ Ошибка настройки TTS: {e}")
    
    def speak(self, text):
        """Озвучивание текста"""
        def speak_thread():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
        
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
    
    def listen(self, timeout=5):
        """Распознавание речи"""
        try:
            with self.microphone as source:
                print("🎤 Слушаю...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=timeout-1
                )
                
                # Пробуем Google распознавание
                try:
                    text = self.recognizer.recognize_google(audio, language='ru-RU')
                    print(f"📝 Распознано: {text}")
                    return text
                except sr.UnknownValueError:
                    print("❌ Не удалось распознать речь")
                    return None
                except sr.RequestError:
                    # Fallback на офлайн
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        return text
                    except:
                        return None
        except sr.WaitTimeoutError:
            print("⏰ Время ожидания истекло")
            return None
        except Exception as e:
            print(f"STT Error: {e}")
            return None
    
    def start_voice_listening(self):
        """Запуск прослушивания голоса"""
        if not self.is_listening:
            self.is_listening = True
            thread = threading.Thread(target=self._listening_loop, daemon=True)
            thread.start()
            print("✅ Голосовое прослушивание запущено")
    
    def stop_voice_listening(self):
        """Остановка прослушивания голоса"""
        self.is_listening = False
        print("⏹️ Голосовое прослушивание остановлено")
    
    def _listening_loop(self):
        """Цикл прослушивания"""
        while self.is_listening:
            text = self.listen(timeout=5)
            if text:
                response = self.process_command(text)
                print(f"Response: {response}")
            time.sleep(0.5)
    
    def process_command(self, command):
        """Обработка команды через ИИ"""
        command_lower = command.lower().strip()
        
        # Приветствие
        if any(word in command_lower for word in ['привет', 'здравствуй', 'hello', 'хай']):
            response = "Привет! Я Raven AI, ваш личный помощник. Чем могу помочь?"
        
        # Системная информация
        elif any(word in command_lower for word in ['система', 'информация', 'состояние', 'cpu', 'ram']):
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C:/' if os.name == 'nt' else '/').percent
            response = f"Системная информация: процессор {cpu}%, память {ram}%, диск {disk}%"
        
        # Время и дата
        elif any(word in command_lower for word in ['время', 'который час', 'дата']):
            now = datetime.now()
            response = f"Сейчас {now.strftime('%H:%M:%S')}, {now.strftime('%d.%m.%Y')}"
        
        # Открытие приложений
        elif any(word in command_lower for word in ['открой', 'запусти']):
            if 'браузер' in command_lower or 'интернет' in command_lower:
                webbrowser.open("https://www.google.com")
                response = "Открываю браузер"
            elif 'блокнот' in command_lower:
                subprocess.Popen(['notepad.exe'])
                response = "Открываю блокнот"
            elif 'калькулятор' in command_lower:
                subprocess.Popen(['calc.exe'])
                response = "Открываю калькулятор"
            elif 'проводник' in command_lower:
                subprocess.Popen(['explorer.exe'])
                response = "Открываю проводник"
            else:
                response = "Какое приложение открыть?"
        
        # Закрытие приложений
        elif any(word in command_lower for word in ['закрой', 'останови']):
            if 'браузер' in command_lower:
                response = "Закрываю браузер"
            elif 'приложение' in command_lower or 'программу' in command_lower:
                response = "Пожалуйста, уточните, какое приложение закрыть"
            else:
                response = "Команда закрытия приложений в разработке"
        
        # Поиск в интернете
        elif 'найди' in command_lower or 'поиск' in command_lower:
            query = command_lower.replace('найди', '').replace('поиск', '').strip()
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                response = f"Ищу информацию по запросу: {query}"
            else:
                response = "Что найти в интернете?"
        
        # Помощь
        elif any(word in command_lower for word in ['помощь', 'помоги', 'что ты умеешь', 'команды']):
            response = """Я умею:
1. Говорить о состоянии системы (CPU, RAM, диск)
2. Открывать приложения (браузер, блокнот, калькулятор)
3. Искать в интернете
4. Сообщать время и дату
5. Выполнять голосовые команды
Просто скажите что вам нужно!"""
        
        # Благодарность
        elif 'спасибо' in command_lower:
            response = "Всегда рад помочь! Есть еще вопросы?"
        
        # Прощание
        elif any(word in command_lower for word in ['пока', 'до свидания', 'выход']):
            response = "До свидания! Буду ждать вашего возвращения."
        
        # Неизвестная команда
        else:
            response = f"Понял команду: '{command}'. В будущем научусь это делать!"
        
        # Сохраняем в историю
        self.command_history.append({
            'time': datetime.now().isoformat(),
            'command': command,
            'response': response
        })
        
        # Ограничиваем историю
        if len(self.command_history) > 50:
            self.command_history = self.command_history[-50:]
        
        # Озвучиваем ответ
        self.speak(response)
        
        return response
    
    def load_skills(self):
        """Загрузка навыков из файла"""
        skills_file = os.path.join('data', 'skills.json')
        default_skills = {
            'system_info': {
                'description': 'Показать информацию о системе',
                'keywords': ['система', 'инфо', 'cpu', 'ram']
            },
            'open_app': {
                'description': 'Открыть приложение',
                'keywords': ['открой', 'запусти']
            },
            'search_web': {
                'description': 'Поиск в интернете',
                'keywords': ['найди', 'поиск']
            }
        }
        
        try:
            if os.path.exists(skills_file):
                with open(skills_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        return default_skills
    
    def save_skills(self):
        """Сохранение навыков"""
        try:
            os.makedirs('data', exist_ok=True)
            skills_file = os.path.join('data', 'skills.json')
            with open(skills_file, 'w', encoding='utf-8') as f:
                json.dump(self.skills, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving skills: {e}")