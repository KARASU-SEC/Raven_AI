// API взаимодействие с Python backend
class PythonBackendAPI {
    constructor() {
        this.baseURL = 'http://localhost:5000';
        this.isConnected = false;
        this.checkConnection();
    }

    async checkConnection() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            if (response.ok) {
                this.isConnected = true;
                console.log('✅ Python backend подключен');
                return true;
            }
        } catch (error) {
            this.isConnected = false;
            console.warn('⚠️ Python backend не доступен');
        }
        return false;
    }

    async getSystemMetrics() {
        try {
            const response = await fetch(`${this.baseURL}/api/system/metrics`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Ошибка получения метрик:', error);
        }
        return null;
    }

    async getProcesses(limit = 20, sortBy = 'cpu') {
        try {
            const response = await fetch(
                `${this.baseURL}/api/system/processes?limit=${limit}&sort_by=${sortBy}`
            );
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Ошибка получения процессов:', error);
        }
        return null;
    }

    async sendCommand(command) {
        try {
            const response = await fetch(`${this.baseURL}/api/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: command })
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Ошибка отправки команды:', error);
        }
        return null;
    }

    async chatWithAI(message, context = []) {
        try {
            const response = await fetch(`${this.baseURL}/api/ai/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, context: context })
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Ошибка чата с ИИ:', error);
        }
        return null;
    }

    async systemAction(action, params = {}) {
        try {
            const response = await fetch(`${this.baseURL}/api/system/actions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: action, params: params })
            });
            
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Ошибка выполнения действия:', error);
        }
        return null;
    }

    async getSystemInfo() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Ошибка получения информации:', error);
        }
        return null;
    }
}

// Создаем глобальный экземпляр API
window.pythonAPI = new PythonBackendAPI();