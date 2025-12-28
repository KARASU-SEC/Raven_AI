// Главный файл приложения Raven AI Karasu
class RavenApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.systemMetrics = null;
        this.pythonStatus = 'checking';
        this.init();
    }

    async init() {
        console.log('🚀 Инициализация Raven AI Karasu...');
        
        // Показываем статус загрузки
        this.updateLoadingStatus('Загрузка приложения...', 20);
        
        // Инициализируем компоненты
        await this.initializeComponents();
        
        this.updateLoadingStatus('Подключение к Python backend...', 40);
        
        // Проверяем Python backend
        await this.checkPythonBackend();
        
        this.updateLoadingStatus('Загрузка интерфейса...', 60);
        
        // Инициализируем страницы
        await this.initializePages();
        
        this.updateLoadingStatus('Настройка обновлений...', 80);
        
        // Настраиваем периодические обновления
        this.setupPeriodicUpdates();
        
        this.updateLoadingStatus('Запуск системы...', 100);
        
        // Запускаем приложение
        setTimeout(() => {
            this.startApplication();
        }, 500);
    }

    updateLoadingStatus(message, progress) {
        const statusEl = document.getElementById('loadingStatus');
        const progressEl = document.querySelector('.progress-fill');
        
        if (statusEl) statusEl.textContent = message;
        if (progressEl) progressEl.style.width = `${progress}%`;
    }

    async initializeComponents() {
        // Здесь будут инициализированы все компоненты
        // Сейчас это заглушка
        return new Promise(resolve => setTimeout(resolve, 500));
    }

    async checkPythonBackend() {
        try {
            const response = await fetch('http://localhost:5000/api/health');
            if (response.ok) {
                const data = await response.json();
                this.pythonStatus = 'connected';
                console.log('✅ Python backend подключен:', data.version);
                return true;
            } else {
                this.pythonStatus = 'error';
                console.warn('⚠️ Python backend не отвечает');
                return false;
            }
        } catch (error) {
            this.pythonStatus = 'error';
            console.error('❌ Ошибка подключения к Python backend:', error);
            return false;
        }
    }

    async initializePages() {
        // Создаем DOM структуру приложения
        this.createAppStructure();
        
        // Инициализируем навигацию
        this.setupNavigation();
        
        // Инициализируем управление окном
        this.setupWindowControls();
        
        // Инициализируем обновление времени
        this.setupTimeUpdates();
    }

    createAppStructure() {
        // Создаем структуру приложения
        const appContainer = document.createElement('div');
        appContainer.className = 'app-container';
        appContainer.id = 'appContainer';
        
        appContainer.innerHTML = `
            <!-- Title Bar -->
            <div class="title-bar">
                <div class="title-left">
                    <div class="logo">鴉</div>
                    <div class="app-name">RAVEN AI KARASU</div>
                    <div class="version">v2.2</div>
                    <div class="title-jp">「精確さの刀」</div>
                </div>
                <div class="window-controls">
                    <button class="window-btn minimize" id="minimizeBtn">−</button>
                    <button class="window-btn maximize" id="maximizeBtn">□</button>
                    <button class="window-btn close" id="closeBtn">✕</button>
                </div>
            </div>

            <!-- Main Container -->
            <div class="main-container">
                <!-- Sidebar -->
                <div class="sidebar" id="sidebar">
                    <div class="nav-section">
                        <div class="nav-header">
                            <span class="jp-text">ナビゲーション</span>
                        </div>
                        <div class="nav-item active" data-page="dashboard">
                            <span class="nav-icon">📊</span>
                            <span class="nav-text">Дашборд</span>
                            <span class="nav-jp">ダッシュボード</span>
                        </div>
                        <div class="nav-item" data-page="voice">
                            <span class="nav-icon">🎤</span>
                            <span class="nav-text">Голос</span>
                            <span class="nav-jp">音声制御</span>
                        </div>
                        <div class="nav-item" data-page="system">
                            <span class="nav-icon">⚙️</span>
                            <span class="nav-text">Система</span>
                            <span class="nav-jp">システム監視</span>
                        </div>
                        <div class="nav-item" data-page="ai">
                            <span class="nav-icon">🤖</span>
                            <span class="nav-text">ИИ Ассистент</span>
                            <span class="nav-jp">AIアシスタント</span>
                        </div>
                        <div class="nav-item" data-page="settings">
                            <span class="nav-icon">🔧</span>
                            <span class="nav-text">Настройки</span>
                            <span class="nav-jp">設定</span>
                        </div>
                    </div>

                    <div class="nav-section">
                        <div class="nav-header">
                            <span class="jp-text">クイックアクション</span>
                        </div>
                        <button class="nav-item" data-action="voice-command">
                            <span class="nav-icon">🎤</span>
                            <span class="nav-text">Голосовая команда</span>
                        </button>
                        <button class="nav-item" data-action="screenshot">
                            <span class="nav-icon">📷</span>
                            <span class="nav-text">Скриншот</span>
                        </button>
                        <button class="nav-item" data-action="clean-ram">
                            <span class="nav-icon">🧹</span>
                            <span class="nav-text">Очистка RAM</span>
                        </button>
                    </div>

                    <div style="margin-top: auto; padding: 20px 16px; border-top: 1px solid var(--karasu-border);">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, var(--karasu-red), var(--karasu-red-dark)); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'Noto Sans JP'; font-size: 20px; color: white;">刀</div>
                            <div style="flex: 1;">
                                <div style="font-size: 14px; font-weight: 600;">Мастер системы</div>
                                <div style="display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--karasu-text-gray);">
                                    <span class="status-indicator connected"></span>
                                    <span>オンライン</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Main Content -->
                <div class="main-content" id="mainContent">
                    <!-- Страницы будут вставлены сюда -->
                </div>
            </div>

            <!-- Status Bar -->
            <div class="status-bar">
                <div class="status-left">
                    <div class="status-item">
                        <span class="status-indicator ${this.pythonStatus === 'connected' ? 'connected' : 'error'}"></span>
                        <span id="backendStatusText">${this.pythonStatus === 'connected' ? 'Python: Подключен' : 'Python: Ошибка'}</span>
                    </div>
                    <div class="status-item">
                        <span class="status-indicator connected"></span>
                        <span>Система: Активна</span>
                    </div>
                </div>
                <div class="status-center">
                    <span id="currentTime">--:--:--</span>
                    <span class="separator">|</span>
                    <span id="currentDate">--.--.----</span>
                </div>
                <div class="status-right">
                    <span class="status-item">
                        <span class="jp-text">「完璧を求めて」</span>
                    </span>
                </div>
            </div>
        `;
        
        document.getElementById('app').appendChild(appContainer);
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item[data-page]');
        const actionItems = document.querySelectorAll('.nav-item[data-action]');
        
        // Навигация по страницам
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const page = item.getAttribute('data-page');
                this.showPage(page);
                
                // Обновляем активный элемент
                navItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
            });
        });
        
        // Быстрые действия
        actionItems.forEach(item => {
            item.addEventListener('click', () => {
                const action = item.getAttribute('data-action');
                this.handleQuickAction(action);
            });
        });
        
        // Показываем начальную страницу
        this.showPage('dashboard');
    }

    setupWindowControls() {
        const minimizeBtn = document.getElementById('minimizeBtn');
        const maximizeBtn = document.getElementById('maximizeBtn');
        const closeBtn = document.getElementById('closeBtn');
        
        if (window.electronAPI) {
            minimizeBtn.addEventListener('click', () => window.electronAPI.minimizeWindow());
            maximizeBtn.addEventListener('click', () => window.electronAPI.maximizeWindow());
            closeBtn.addEventListener('click', () => window.electronAPI.closeWindow());
        } else {
            // Fallback для браузера
            minimizeBtn.addEventListener('click', () => console.log('Minimize'));
            maximizeBtn.addEventListener('click', () => {
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                } else {
                    document.exitFullscreen();
                }
            });
            closeBtn.addEventListener('click', () => console.log('Close'));
        }
    }

    setupTimeUpdates() {
        this.updateDateTime();
        setInterval(() => this.updateDateTime(), 1000);
    }

    updateDateTime() {
        const now = new Date();
        const timeEl = document.getElementById('currentTime');
        const dateEl = document.getElementById('currentDate');
        
        if (timeEl) {
            timeEl.textContent = now.toLocaleTimeString('ru-RU', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
        }
        
        if (dateEl) {
            dateEl.textContent = now.toLocaleDateString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        }
    }

    async showPage(pageId) {
        this.currentPage = pageId;
        
        // Обновляем заголовок
        const pageTitles = {
            dashboard: 'Дашборд',
            voice: 'Голосовое управление',
            system: 'Мониторинг системы',
            ai: 'ИИ Ассистент',
            settings: 'Настройки'
        };
        
        // Загружаем страницу
        const mainContent = document.getElementById('mainContent');
        if (mainContent) {
            mainContent.innerHTML = '';
            
            // Показываем индикатор загрузки
            const loading = document.createElement('div');
            loading.className = 'karasu-card';
            loading.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div class="kanji-loading" style="font-size: 40px; margin-bottom: 20px;">鴉</div>
                    <h3>Загрузка ${pageTitles[pageId]}...</h3>
                    <div class="jp-text" style="margin-top: 10px;">読み込み中...</div>
                </div>
            `;
            mainContent.appendChild(loading);
            
            // Загружаем содержимое страницы
            try {
                let pageContent;
                switch(pageId) {
                    case 'dashboard':
                        pageContent = await this.loadDashboard();
                        break;
                    case 'voice':
                        pageContent = await this.loadVoicePage();
                        break;
                    case 'system':
                        pageContent = await this.loadSystemPage();
                        break;
                    case 'ai':
                        pageContent = await this.loadAIPage();
                        break;
                    case 'settings':
                        pageContent = await this.loadSettingsPage();
                        break;
                    default:
                        pageContent = await this.loadDashboard();
                }
                
                // Заменяем индикатор загрузки на содержимое страницы
                setTimeout(() => {
                    mainContent.innerHTML = pageContent;
                    this.initializePageComponents(pageId);
                }, 300);
                
            } catch (error) {
                console.error(`Ошибка загрузки страницы ${pageId}:`, error);
                mainContent.innerHTML = `
                    <div class="karasu-card" style="text-align: center; padding: 40px; color: var(--karasu-error);">
                        <h3>❌ Ошибка загрузки</h3>
                        <p>Не удалось загрузить страницу ${pageTitles[pageId]}</p>
                        <button onclick="window.location.reload()" style="margin-top: 20px; padding: 10px 20px; background: var(--karasu-red); color: white; border: none; border-radius: 6px; cursor: pointer;">Перезагрузить</button>
                    </div>
                `;
            }
        }
    }

    async handleQuickAction(action) {
        switch(action) {
            case 'voice-command':
                this.showNotification('🎤 Запуск голосовой команды...', 'info');
                // Здесь будет вызов голосового управления
                break;
            case 'screenshot':
                this.showNotification('📷 Создание скриншота...', 'info');
                // Здесь будет создание скриншота
                break;
            case 'clean-ram':
                this.showNotification('🧹 Очистка оперативной памяти...', 'info');
                await this.cleanRAM();
                break;
        }
    }

    async cleanRAM() {
        try {
            const response = await fetch('http://localhost:5000/api/system/actions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'clean_ram' })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showNotification(`✅ ${data.result.message}`, 'success');
            } else {
                this.showNotification('❌ Не удалось очистить RAM', 'error');
            }
        } catch (error) {
            this.showNotification('❌ Ошибка подключения к API', 'error');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.style.cssText = `
            position: fixed;
            top: 50px;
            right: 20px;
            background: linear-gradient(135deg, var(--karasu-gray), var(--karasu-darker));
            border: 1px solid var(--karasu-border);
            border-left: 4px solid ${type === 'success' ? 'var(--karasu-success)' : type === 'error' ? 'var(--karasu-error)' : type === 'warning' ? 'var(--karasu-warning)' : 'var(--karasu-info)'};
            border-radius: 8px;
            padding: 16px;
            min-width: 300px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            animation: slideIn 0.3s ease;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        
        notification.innerHTML = `
            <span style="font-size: 20px;">${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}</span>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматическое скрытие через 3 секунды
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    setupPeriodicUpdates() {
        // Обновление метрик каждые 5 секунд
        setInterval(() => {
            if (this.currentPage === 'dashboard') {
                this.updateDashboardMetrics();
            }
        }, 5000);
        
        // Проверка состояния Python каждые 10 секунд
        setInterval(async () => {
            const connected = await this.checkPythonBackend();
            const statusEl = document.getElementById('backendStatusText');
            const indicator = document.querySelector('.status-indicator');
            
            if (statusEl && indicator) {
                if (connected) {
                    statusEl.textContent = 'Python: Подключен';
                    indicator.className = 'status-indicator connected';
                } else {
                    statusEl.textContent = 'Python: Ошибка';
                    indicator.className = 'status-indicator error';
                }
            }
        }, 10000);
    }

    startApplication() {
        const loadingScreen = document.getElementById('loadingScreen');
        const appContainer = document.getElementById('appContainer');
        
        // Скрываем экран загрузки
        if (loadingScreen) {
            loadingScreen.style.opacity = '0';
            setTimeout(() => {
                loadingScreen.style.display = 'none';
            }, 500);
        }
        
        // Показываем приложение
        if (appContainer) {
            appContainer.style.display = 'flex';
            setTimeout(() => {
                appContainer.style.opacity = '1';
            }, 10);
        }
        
        // Обновляем метрики
        this.updateDashboardMetrics();
        
        // Показываем приветственное уведомление
        setTimeout(() => {
            this.showNotification('🚀 Raven AI Karasu успешно запущен!', 'success');
        }, 1000);
    }
}

// Запуск приложения при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.ravenApp = new RavenApp();
});