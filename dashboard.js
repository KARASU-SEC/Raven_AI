// Страница дашборда
RavenApp.prototype.loadDashboard = async function() {
    return `
        <div class="dashboard-page">
            <!-- Заголовок страницы -->
            <div class="page-header">
                <h1><i class="fas fa-tachometer-alt"></i> Дашборд</h1>
                <div class="page-subtitle">「システムダッシュボード」</div>
            </div>

            <!-- Ключевые метрики -->
            <div class="metrics-grid" id="metricsGrid">
                <!-- Метрики будут обновляться динамически -->
            </div>

            <!-- График и чат -->
            <div class="dashboard-row">
                <div class="karasu-card" style="flex: 2;">
                    <div class="card-header">
                        <h3><i class="fas fa-chart-line"></i> Нагрузка системы</h3>
                        <div class="jp-sub">システムロード</div>
                    </div>
                    <div class="chart-container" style="height: 300px;">
                        <canvas id="systemChart"></canvas>
                    </div>
                </div>
                
                <div class="karasu-card" style="flex: 1;">
                    <div class="card-header">
                        <h3><i class="fas fa-robot"></i> Быстрые команды</h3>
                        <div class="jp-sub">クイックコマンド</div>
                    </div>
                    <div class="quick-commands">
                        <button class="quick-command" data-command="системная информация">
                            <span class="command-icon"><i class="fas fa-info-circle"></i></span>
                            <span class="command-text">Системная информация</span>
                        </button>
                        <button class="quick-command" data-command="время">
                            <span class="command-icon"><i class="fas fa-clock"></i></span>
                            <span class="command-text">Текущее время</span>
                        </button>
                        <button class="quick-command" data-command="открой браузер">
                            <span class="command-icon"><i class="fas fa-globe"></i></span>
                            <span class="command-text">Открыть браузер</span>
                        </button>
                        <button class="quick-command" data-command="сделай скриншот">
                            <span class="command-icon"><i class="fas fa-camera"></i></span>
                            <span class="command-text">Скриншот</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Процессы и действия -->
            <div class="dashboard-row">
                ${window.systemProcesses.createProcessesTable()}
                
                <div class="karasu-card">
                    <div class="card-header">
                        <h3><i class="fas fa-bolt"></i> Быстрые действия</h3>
                        <div class="jp-sub">クイックアクション</div>
                    </div>
                    <div class="quick-actions">
                        <button class="quick-action" data-action="voice-test">
                            <span class="action-icon"><i class="fas fa-microphone"></i></span>
                            <span class="action-text">Тест микрофона</span>
                        </button>
                        <button class="quick-action" data-action="clean-temp">
                            <span class="action-icon"><i class="fas fa-broom"></i></span>
                            <span class="action-text">Очистка временных файлов</span>
                        </button>
                        <button class="quick-action" data-action="network-info">
                            <span class="action-icon"><i class="fas fa-wifi"></i></span>
                            <span class="action-text">Информация о сети</span>
                        </button>
                        <button class="quick-action" data-action="update-check">
                            <span class="action-icon"><i class="fas fa-sync-alt"></i></span>
                            <span class="action-text">Проверить обновления</span>
                        </button>
                    </div>
                </div>
            </div>

            <!-- Статистика -->
            <div class="karasu-card" style="margin-top: 20px;">
                <div class="card-header">
                    <h3><i class="fas fa-chart-bar"></i> Статистика системы</h3>
                    <div class="jp-sub">システム統計</div>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-label">Время работы</div>
                        <div class="stat-value" id="uptimeStat">--</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Загрузок CPU</div>
                        <div class="stat-value" id="cpuLoadStat">--</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Свободно RAM</div>
                        <div class="stat-value" id="freeRamStat">--</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Свободно Disk</div>
                        <div class="stat-value" id="freeDiskStat">--</div>
                    </div>
                </div>
            </div>
        </div>
    `;
};

RavenApp.prototype.initializePageComponents = function(pageId) {
    if (pageId === 'dashboard') {
        this.initializeDashboard();
    }
};

RavenApp.prototype.initializeDashboard = function() {
    // Инициализируем сетку метрик
    this.initializeMetricsGrid();
    
    // Создаем график
    window.systemMetrics.createChart('systemChart');
    
    // Загружаем процессы
    window.systemProcesses.updateProcessesList(10);
    
    // Настраиваем обработчики
    this.setupDashboardHandlers();
    
    // Обновляем метрики
    this.updateDashboardMetrics();
};

RavenApp.prototype.initializeMetricsGrid = function() {
    const grid = document.getElementById('metricsGrid');
    if (!grid) return;
    
    grid.innerHTML = `
        ${window.systemMetrics.createMetricCard('CPU', '--%', '💻', '#e63946')}
        ${window.systemMetrics.createMetricCard('RAM', '--%', '🧠', '#3498db')}
        ${window.systemMetrics.createMetricCard('Диск', '--%', '💾', '#9b59b6')}
        ${window.systemMetrics.createMetricCard('Процессы', '--', '⚙️', '#2ecc71')}
    `;
    
    // Добавляем id для элементов
    const cards = grid.querySelectorAll('.metric-card');
    if (cards[0]) {
        cards[0].querySelector('.metric-value').id = 'cpuMetric';
        cards[0].querySelector('.progress-fill').id = 'cpuProgress';
    }
    if (cards[1]) {
        cards[1].querySelector('.metric-value').id = 'ramMetric';
        cards[1].querySelector('.progress-fill').id = 'ramProgress';
    }
    if (cards[2]) {
        cards[2].querySelector('.metric-value').id = 'diskMetric';
        cards[2].querySelector('.progress-fill').id = 'diskProgress';
    }
    if (cards[3]) {
        cards[3].querySelector('.metric-value').id = 'processMetric';
    }
};

RavenApp.prototype.setupDashboardHandlers = function() {
    // Быстрые команды
    document.querySelectorAll('.quick-command').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const command = e.currentTarget.getAttribute('data-command');
            this.showNotification(`Выполнение команды: ${command}`, 'info');
            
            const result = await window.pythonAPI.sendCommand(command);
            if (result && result.success) {
                this.showNotification(`✅ ${result.response}`, 'success');
            }
        });
    });
    
    // Быстрые действия
    document.querySelectorAll('.quick-action').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const action = e.currentTarget.getAttribute('data-action');
            this.handleQuickAction(action);
        });
    });
    
    // Обновление процессов
    const refreshBtn = document.getElementById('refreshProcesses');
    const limitSelect = document.getElementById('processLimit');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            const limit = limitSelect ? parseInt(limitSelect.value) : 10;
            window.systemProcesses.updateProcessesList(limit);
        });
    }
    
    if (limitSelect) {
        limitSelect.addEventListener('change', () => {
            const limit = parseInt(limitSelect.value);
            window.systemProcesses.updateProcessesList(limit);
        });
    }
};

RavenApp.prototype.updateDashboardMetrics = async function() {
    const metrics = await window.systemMetrics.updateMetricsDisplay();
    if (metrics) {
        // Обновляем статистику
        this.updateStats(metrics);
    }
};

RavenApp.prototype.updateStats = function(metrics) {
    // Время работы (имитация)
    const uptimeEl = document.getElementById('uptimeStat');
    if (uptimeEl) {
        const hours = Math.floor(Math.random() * 24);
        const minutes = Math.floor(Math.random() * 60);
        uptimeEl.textContent = `${hours}ч ${minutes}м`;
    }
    
    // Загрузка CPU
    const cpuLoadEl = document.getElementById('cpuLoadStat');
    if (cpuLoadEl && metrics.cpu) {
        cpuLoadEl.textContent = `${metrics.cpu.cores} ядер, ${metrics.cpu.percent.toFixed(1)}%`;
    }
    
    // Свободная RAM
    const freeRamEl = document.getElementById('freeRamStat');
    if (freeRamEl && metrics.ram) {
        const freeGB = (metrics.ram.free_gb || 0).toFixed(1);
        freeRamEl.textContent = `${freeGB} GB`;
    }
    
    // Свободный Disk
    const freeDiskEl = document.getElementById('freeDiskStat');
    if (freeDiskEl && metrics.disk) {
        const freeGB = (metrics.disk.free_gb || 0).toFixed(1);
        freeDiskEl.textContent = `${freeGB} GB`;
    }
};