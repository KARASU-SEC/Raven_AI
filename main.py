#!/usr/bin/env python3
"""
Raven AI v2.2 - Backend API для Electron приложения
"""
import sys
import os
import threading

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.raven_ai import RavenAI
    from core.neural_tts import HumanVoiceTTS
    from core.stt_enhanced import EnhancedSTT
    from core.neural_core import NeuralCore
    from ai_api import AIAPI
    
    # Импортируем Flask для API
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    print("✅ Все модули загружены успешно")
except ImportError as e:
    print(f"⚠️ Ошибка импорта: {e}")
    print("Установите зависимости: pip install -r requirements.txt")
    sys.exit(1)

def create_backend_api():
    """Создание Flask API для Electron"""
    app = Flask(__name__)
    CORS(app)  # Разрешаем CORS для Electron
    
    # Инициализация компонентов Raven AI
    raven = RavenAI()
    tts = HumanVoiceTTS() if 'HumanVoiceTTS' in globals() else None
    stt = EnhancedSTT() if 'EnhancedSTT' in globals() else None
    neural_core = NeuralCore() if 'NeuralCore' in globals() else None
    
    # Инициализация AI API
    ai_api = AIAPI(raven)
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Проверка состояния сервера"""
        return jsonify({
            'status': 'online',
            'service': 'Raven AI Backend',
            'version': '2.2.0',
            'raven_initialized': raven is not None,
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/metrics', methods=['GET'])
    def get_metrics():
        """Получение метрик системы"""
        import psutil
        from datetime import datetime
        
        cpu_percent = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('C:/' if os.name == 'nt' else '/')
        
        metrics = {
            'cpu': {
                'percent': cpu_percent,
                'cores': psutil.cpu_count()
            },
            'ram': {
                'percent': ram.percent,
                'total': ram.total,
                'used': ram.used,
                'free': ram.free
            },
            'disk': {
                'percent': disk.percent,
                'total': disk.total,
                'used': disk.used,
                'free': disk.free
            },
            'processes': len(psutil.pids()),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(metrics)
    
    @app.route('/api/command', methods=['POST'])
    def process_command():
        """Обработка команды"""
        data = request.json
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        try:
            response = raven.process_command(command)
            return jsonify({
                'success': True,
                'response': response,
                'command': command
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'command': command
            }), 500
    
    # Регистрируем AI endpoints
    ai_api.register_endpoints(app)
    
    return app

def main():
    """Точка входа в приложение"""
    print("🚀 Запуск Raven AI Backend API v2.2...")
    
    # Создаем Flask приложение
    app = create_backend_api()
    
    # Запускаем Flask в отдельном потоке
    def run_flask():
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    print("✅ Backend API запущен на http://127.0.0.1:5000")
    print("📡 AI Endpoints:")
    print("   POST /api/ai/chat        - Чат с ИИ")
    print("   GET  /api/ai/models      - Список моделей")
    print("   GET  /api/ai/history     - История чата")
    print("   POST /api/ai/analyze     - Анализ текста")
    print("   POST /api/ai/summarize   - Суммаризация")
    print("   POST /api/ai/translate   - Перевод")
    print("=" * 50)
    
    # Держим основной поток активным
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Остановка Raven AI Backend...")
        sys.exit(0)

if __name__ == "__main__":
    main()