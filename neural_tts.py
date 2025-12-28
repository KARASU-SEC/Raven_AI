"""
Нейросетевой TTS с человеческим голосом (упрощённая версия)
"""
import pyttsx3
import threading
import queue
import os
import json
from typing import Optional

class HumanVoiceTTS:
    """TTS с человеческим голосом"""
    
    def __init__(self):
        self.voices = {}
        self.current_voice = 'david'
        self.emotion = 'neutral'
        self.speech_rate = 170
        self.volume = 0.9
        
        # Очередь для асинхронного воспроизведения
        self.queue = queue.Queue()
        self.is_speaking = False
        
        # Инициализация голосов
        self.init_voices()
        
        # Поток воспроизведения
        self.playback_thread = threading.Thread(target=self._playback_worker, daemon=True)
        self.playback_thread.start()
        
        print("🎵 Human Voice TTS инициализирован")
    
    def init_voices(self):
        """Инициализация голосовых профилей"""
        try:
            engine = pyttsx3.init(driverName='sapi5')
            sapi_voices = engine.getProperty('voices')
            
            for voice in sapi_voices:
                voice_name = voice.name.lower()
                
                # Русские голоса
                if 'russian' in voice_name or 'rus' in voice.id.lower():
                    if 'male' in voice_name or 'муж' in voice_name:
                        self.voices['david'] = {
                            'name': 'David (Russian)',
                            'id': voice.id,
                            'gender': 'male',
                            'engine': 'sapi5'
                        }
                    elif 'female' in voice_name or 'жен' in voice_name:
                        self.voices['irina'] = {
                            'name': 'Irina (Russian)',
                            'id': voice.id,
                            'gender': 'female',
                            'engine': 'sapi5'
                        }
                
                # Английские голоса
                elif 'microsoft david desktop' in voice_name:
                    self.voices['david_en'] = {
                        'name': 'David EN',
                        'id': voice.id,
                        'gender': 'male',
                        'engine': 'sapi5'
                    }
                elif 'microsoft zira desktop' in voice_name:
                    self.voices['zira'] = {
                        'name': 'Zira',
                        'id': voice.id,
                        'gender': 'female',
                        'engine': 'sapi5'
                    }
            
            engine.stop()
            
            # Если не нашли русские голоса, используем первый доступный
            if not self.voices:
                self.voices['default'] = {
                    'name': 'Default',
                    'id': sapi_voices[0].id,
                    'gender': 'unknown',
                    'engine': 'sapi5'
                }
                self.current_voice = 'default'
                
        except Exception as e:
            print(f"⚠️ Ошибка загрузки голосов: {e}")
            # Запасной вариант
            self.voices['fallback'] = {
                'name': 'Fallback',
                'id': None,
                'gender': 'unknown',
                'engine': 'pyttsx3'
            }
            self.current_voice = 'fallback'
    
    def speak(self, text: str, voice: Optional[str] = None, 
              emotion: Optional[str] = None, callback: Optional[callable] = None):
        """Произнесение текста"""
        if not text or not text.strip():
            return
            
        # Очистка текста
        text = self.clean_text(text)
        
        # Применение эмоции
        if emotion:
            text = self.apply_emotion(text, emotion)
        
        # Выбор голоса
        voice_name = voice or self.current_voice
        voice_profile = self.voices.get(voice_name, list(self.voices.values())[0])
        
        # Добавление в очередь
        self.queue.put((text, voice_profile, callback))
    
    def clean_text(self, text: str) -> str:
        """Очистка текста для TTS"""
        import re
        # Удаляем специальные символы, но оставляем знаки препинания
        text = re.sub(r'[^\w\s.,!?а-яА-ЯёЁ\-]', ' ', text)
        # Заменяем множественные пробелы на один
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def apply_emotion(self, text: str, emotion: str) -> str:
        """Применение эмоциональной окраски к тексту"""
        emotional_prefixes = {
            'happy': ['Отлично! ', 'Замечательно! ', 'Рад сообщить: '],
            'sad': ['К сожалению, ', 'Извините, но ', 'Печальная новость: '],
            'excited': ['Внимание! ', 'Удивительно! ', 'Потрясающе! '],
            'calm': ['Хорошо. ', 'Как скажете. ', 'Принято. '],
            'surprised': ['Ого! ', 'Неожиданно! ', 'Удивительно: ']
        }
        
        import random
        if emotion in emotional_prefixes:
            prefix = random.choice(emotional_prefixes[emotion])
            return prefix + text
        
        return text
    
    def _playback_worker(self):
        """Рабочий поток для воспроизведения"""
        while True:
            try:
                text, voice_profile, callback = self.queue.get()
                if text is None:  # Сигнал остановки
                    break
                    
                self.is_speaking = True
                self._speak_sync(text, voice_profile)
                
                if callback:
                    callback()
                    
                self.is_speaking = False
                self.queue.task_done()
                
            except Exception as e:
                print(f"❌ Ошибка воспроизведения: {e}")
                self.is_speaking = False
    
    def _speak_sync(self, text: str, voice_profile: dict):
        """Синхронное воспроизведение"""
        try:
            engine = pyttsx3.init(driverName='sapi5')
            
            # Установка голоса
            if voice_profile.get('id'):
                engine.setProperty('voice', voice_profile['id'])
            
            # Настройки
            engine.setProperty('rate', self.speech_rate)
            engine.setProperty('volume', self.volume)
            
            # Произнесение
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            
        except Exception as e:
            print(f"❌ Ошибка TTS: {e}")
            # Аварийный fallback
            try:
                import winsound
                winsound.MessageBeep()
            except:
                pass
    
    def set_voice(self, voice_name: str) -> bool:
        """Установка голоса по имени"""
        if voice_name in self.voices:
            self.current_voice = voice_name
            return True
        return False
    
    def set_emotion(self, emotion: str):
        """Установка эмоции"""
        valid_emotions = ['neutral', 'happy', 'sad', 'excited', 'calm', 'surprised']
        if emotion in valid_emotions:
            self.emotion = emotion
    
    def set_speech_rate(self, rate: int):
        """Установка скорости речи"""
        self.speech_rate = max(50, min(300, rate))
    
    def set_volume(self, volume: float):
        """Установка громкости"""
        self.volume = max(0.0, min(1.0, volume))
    
    def get_available_voices(self) -> list:
        """Получение списка доступных голосов"""
        return [{
            'id': voice_id,
            'name': info['name'],
            'gender': info.get('gender', 'unknown')
        } for voice_id, info in self.voices.items()]
    
    def stop(self):
        """Остановка воспроизведения"""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                break
        
        self.queue.put((None, None, None))