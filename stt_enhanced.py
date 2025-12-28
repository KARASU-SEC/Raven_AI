"""
Улучшенное распознавание речи с несколькими движками и обработкой ошибок
"""
import speech_recognition as sr
import vosk
import json
import os
import time
from typing import Optional
import threading

class EnhancedSTT:
    """Улучшенное распознавание речи с поддержкой офлайн/онлайн движков"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Инициализация Vosk для офлайн распознавания
        self.vosk_model = None
        self._init_vosk()
        
        # Настройки
        self.preferred_engine = "google"  # google, vosk, sphinx
        
        # Кэш для результатов
        self.last_result = None
        
        print("✅ Enhanced STT инициализирован")
    
    def _init_vosk(self):
        """Инициализация Vosk модели"""
        try:
            model_path = os.path.join('models', 'vosk-model-small-ru-0.22')
            if os.path.exists(model_path):
                self.vosk_model = vosk.Model(model_path)
                print("✅ Vosk модель загружена")
            else:
                print("⚠️ Vosk модель не найдена, используется только онлайн распознавание")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки Vosk: {e}")
    
    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """Прослушивание и распознавание речи"""
        try:
            with self.microphone as source:
                print("🎤 Слушаю...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            # Пробуем разные движки в порядке предпочтения
            engines = [
                ("google", self._recognize_google),
                ("vosk", self._recognize_vosk),
                ("sphinx", self._recognize_sphinx)
            ]
            
            for engine_name, engine_func in engines:
                if engine_name == "vosk" and not self.vosk_model:
                    continue
                    
                try:
                    result = engine_func(audio)
                    if result and result.strip():
                        print(f"✅ {engine_name.capitalize()}: '{result}'")
                        self.last_result = result
                        return result
                except Exception as e:
                    print(f"⚠️ {engine_name.capitalize()} ошибка: {e}")
                    continue
            
            return None
            
        except sr.WaitTimeoutError:
            print("⏰ Время ожидания истекло")
            return None
        except Exception as e:
            print(f"❌ Ошибка прослушивания: {e}")
            return None
    
    def _recognize_google(self, audio) -> Optional[str]:
        """Распознавание через Google"""
        try:
            return self.recognizer.recognize_google(audio, language='ru-RU')
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"⚠️ Google API недоступен: {e}")
            return None
    
    def _recognize_vosk(self, audio) -> Optional[str]:
        """Офлайн распознавание через Vosk"""
        if not self.vosk_model:
            return None
        
        try:
            audio_data = audio.get_raw_data()
            rec = vosk.KaldiRecognizer(self.vosk_model, audio.sample_rate)
            
            if rec.AcceptWaveform(audio_data):
                result = json.loads(rec.Result())
                text = result.get('text', '').strip()
                return text if text else None
        except Exception as e:
            print(f"⚠️ Vosk ошибка: {e}")
        
        return None
    
    def _recognize_sphinx(self, audio) -> Optional[str]:
        """Распознавание через CMU Sphinx"""
        try:
            return self.recognizer.recognize_sphinx(audio)
        except:
            return None
    
    def set_preferred_engine(self, engine: str):
        """Установка предпочтительного движка"""
        valid_engines = ["google", "vosk", "sphinx"]
        if engine in valid_engines:
            self.preferred_engine = engine
            return True
        return False
    
    def get_available_engines(self):
        """Получить список доступных движков"""
        engines = ["google", "sphinx"]
        if self.vosk_model:
            engines.append("vosk")
        return engines