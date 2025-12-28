"""
Расширенный Python API сервер с интеграцией всех модулей Raven AI
"""
import sys
import os
import json
from datetime import datetime

# Добавляем пути для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from flask import Flask, jsonify, request
from flask_cors import CORS
import psutil
import platform

app = Flask(__name__)
CORS(app)

# Переменные для хранения экземпляров
raven_ai = None
neural_core = None

def initialize_ai_modules():
    """Инициализация модулей ИИ"""
    global raven_ai, neural_core
    
    try:
        # Ленивая загрузка модулей
        from core.raven_ai import RavenAI
        from core.neural_core import NeuralCore
        
        print("Инициализация Raven AI...")
        raven_ai = RavenAI()
        
        print("Инициализация Neural Core...")
        neural_core = NeuralCore()
        
        print("✅ AI модули инициализированы")
        return True
        
    except ImportError as e:
        print(f"⚠️ Не удалось загрузить AI модули: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

# Проверяем инициализацию при запуске
ai_initialized = initialize_ai_modules()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка состояния сервера"""
    return jsonify({
        'status': 'online',
        'service': 'Raven AI Backend',
        'version': '2.2.0',
        'python_version': platform.python_version(),
        'ai_initialized': ai_initialized,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/command', methods=['POST'])
def process_command():
    """Обработка команды через ИИ"""
    data = request.json
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    
    try:
        response = ""
        
        # Используем Raven AI если доступен
        if raven_ai:
            response = raven_ai.process_command(command)
        elif neural_core:
            result = neural_core.process_query(command)
            response = result.get('response', 'Команда обработана')
        else:
            response = f"Получена команда: {command}"
        
        return jsonify({
            'success': True,
            'response': response,
            'command': command,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'command': command
        }), 500

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """Чат с ИИ"""
    data = request.json
    message = data.get('message', '').strip()
    context = data.get('context', [])
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        if neural_core:
            result = neural_core.process_query(message, context)
            return jsonify(result)
        else:
            return jsonify({
                'response': 'ИИ модуль не доступен. Это демо-ответ.',
                'intent': 'unknown',
                'emotion': 'neutral',
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'response': 'Произошла ошибка при обработке запроса'
        }), 500

@app.route('/api/system/metrics', methods=['GET'])
def get_system_metrics():
    """Получение метрик системы"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('C:/' if platform.system() == 'Windows' else '/')
        
        return jsonify({
            'cpu': {
                'percent': cpu_percent,
                'cores': psutil.cpu_count(),
                'frequency': psutil.cpu_freq().current if hasattr(psutil.cpu_freq(), 'current') else None
            },
            'ram': {
                'percent': ram.percent,
                'total_gb': round(ram.total / (1024**3), 2),
                'used_gb': round(ram.used / (1024**3), 2),
                'free_gb': round(ram.free / (1024**3), 2)
            },
            'disk': {
                'percent': disk.percent,
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2)
            },
            'processes': len(psutil.pids()),
            'network': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/processes', methods=['GET'])
def get_system_processes():
    """Получение списка процессов"""
    try:
        limit = request.args.get('limit', default=20, type=int)
        sort_by = request.args.get('sort_by', default='cpu')
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'][:50],  # Ограничиваем длину имени
                    'cpu': round(info['cpu_percent'] or 0, 2),
                    'memory': round(info['memory_percent'] or 0, 2),
                    'status': info['status'],
                    'memory_bytes': proc.memory_info().rss if hasattr(proc, 'memory_info') else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            
            if len(processes) >= limit:
                break
        
        # Сортировка
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu'], reverse=True)
        elif sort_by == 'memory':
            processes.sort(key=lambda x: x['memory'], reverse=True)
        elif sort_by == 'name':
            processes.sort(key=lambda x: x['name'].lower())
        
        return jsonify({
            'processes': processes,
            'total': len(processes),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/actions', methods=['POST'])
def system_actions():
    """Системные действия"""
    data = request.json
    action = data.get('action', '')
    
    actions = {
        'clean_ram': clean_ram,
        'get_system_info': get_system_info,
        'kill_process': kill_process
    }
    
    if action in actions:
        try:
            result = actions[action](data.get('params', {}))
            return jsonify({
                'success': True,
                'action': action,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'action': action,
                'error': str(e)
            }), 500
    else:
        return jsonify({
            'success': False,
            'error': f'Действие "{action}" не поддерживается'
        }), 400

def clean_ram(params):
    """Очистка RAM"""
    import gc
    gc.collect()
    return {'message': 'RAM очищена', 'details': 'Garbage collector запущен'}

def get_system_info(params):
    """Получение информации о системе"""
    import socket
    import getpass
    
    return {
        'hostname': socket.gethostname(),
        'username': getpass.getuser(),
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.architecture()[0],
        'processor': platform.processor(),
        'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
    }

def kill_process(params):
    """Завершение процесса"""
    pid = params.get('pid')
    if not pid:
        raise ValueError('Не указан PID процесса')
    
    try:
        process = psutil.Process(pid)
        process.terminate()
        return {'message': f'Процесс {pid} ({process.name()}) завершен'}
    except psutil.NoSuchProcess:
        raise ValueError(f'Процесс с PID {pid} не найден')
    except psutil.AccessDenied:
        raise ValueError(f'Нет прав для завершения процесса {pid}')

if __name__ == '__main__':
    # Настройка кодировки для Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("Raven AI Karasu - Расширенный Backend API")
    print("=" * 60)
    print(f"AI модули: {'✅ Инициализированы' if ai_initialized else '⚠️ Не доступны'}")
    print("📡 Сервер доступен по адресу: http://localhost:5000")
    print("\n🔗 API Endpoints:")
    print("   GET  /api/health             - Проверка состояния")
    print("   POST /api/command            - Обработка команды")
    print("   POST /api/ai/chat            - Чат с ИИ")
    print("   GET  /api/system/metrics     - Метрики системы")
    print("   GET  /api/system/processes   - Список процессов")
    print("   POST /api/system/actions     - Системные действия")
    print("=" * 60)
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        threaded=True
    )