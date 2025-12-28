// Компонент для отображения и управления процессами
class SystemProcesses {
    constructor() {
        this.processList = [];
        this.sortColumn = 'cpu';
        this.sortDirection = 'desc';
    }

    async updateProcessesList(limit = 10) {
        const data = await window.pythonAPI.getProcesses(limit, this.sortColumn);
        if (data && data.processes) {
            this.processList = data.processes;
            this.renderProcesses();
            return data.processes;
        }
        return [];
    }

    renderProcesses() {
        const container = document.getElementById('processesContainer');
        if (!container) return;

        // Сортируем процессы
        const sortedProcesses = [...this.processList].sort((a, b) => {
            const aValue = a[this.sortColumn];
            const bValue = b[this.sortColumn];
            
            if (this.sortDirection === 'desc') {
                return bValue - aValue;
            } else {
                return aValue - bValue;
            }
        });

        container.innerHTML = `
            <div class="processes-header">
                <div class="process-column sortable" data-column="name" style="flex: 2;">
                    <span>Процесс</span>
                    ${this.sortColumn === 'name' ? (this.sortDirection === 'desc' ? '▼' : '▲') : ''}
                </div>
                <div class="process-column sortable" data-column="pid">
                    <span>PID</span>
                    ${this.sortColumn === 'pid' ? (this.sortDirection === 'desc' ? '▼' : '▲') : ''}
                </div>
                <div class="process-column sortable" data-column="cpu" style="color: #e63946;">
                    <span>CPU</span>
                    ${this.sortColumn === 'cpu' ? (this.sortDirection === 'desc' ? '▼' : '▲') : ''}
                </div>
                <div class="process-column sortable" data-column="memory" style="color: #3498db;">
                    <span>RAM</span>
                    ${this.sortColumn === 'memory' ? (this.sortDirection === 'desc' ? '▼' : '▲') : ''}
                </div>
                <div class="process-column" style="width: 100px;">Действия</div>
            </div>
            <div class="processes-list">
                ${sortedProcesses.map(process => this.renderProcessRow(process)).join('')}
            </div>
        `;

        // Добавляем обработчики сортировки
        container.querySelectorAll('.sortable').forEach(column => {
            column.addEventListener('click', (e) => {
                const columnName = e.currentTarget.getAttribute('data-column');
                this.sortByColumn(columnName);
            });
        });

        // Добавляем обработчики кнопок
        container.querySelectorAll('.process-kill-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const pid = parseInt(e.currentTarget.getAttribute('data-pid'));
                this.killProcess(pid);
            });
        });
    }

    renderProcessRow(process) {
        const cpuColor = process.cpu > 70 ? '#e74c3c' : process.cpu > 30 ? '#f39c12' : '#27ae60';
        const memoryColor = process.memory > 70 ? '#e74c3c' : process.memory > 30 ? '#f39c12' : '#27ae60';
        
        return `
            <div class="process-row">
                <div class="process-cell" style="flex: 2;">
                    <span class="process-name" title="${process.name}">${process.name}</span>
                </div>
                <div class="process-cell">${process.pid}</div>
                <div class="process-cell" style="color: ${cpuColor};">
                    ${process.cpu.toFixed(1)}%
                </div>
                <div class="process-cell" style="color: ${memoryColor};">
                    ${process.memory.toFixed(1)}%
                </div>
                <div class="process-cell">
                    <button class="process-kill-btn" data-pid="${process.pid}" 
                            style="padding: 4px 12px; background: rgba(231, 57, 70, 0.1); border: 1px solid #e63946; border-radius: 4px; color: #e63946; font-size: 12px; cursor: pointer;">
                        Завершить
                    </button>
                </div>
            </div>
        `;
    }

    sortByColumn(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'desc' ? 'asc' : 'desc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'desc';
        }
        this.renderProcesses();
    }

    async killProcess(pid) {
        if (!confirm(`Завершить процесс ${pid}?`)) return;
        
        const result = await window.pythonAPI.systemAction('kill_process', { pid: pid });
        if (result && result.success) {
            window.ravenApp.showNotification(`✅ Процесс ${pid} завершен`, 'success');
            this.updateProcessesList();
        } else {
            window.ravenApp.showNotification(`❌ Не удалось завершить процесс ${pid}`, 'error');
        }
    }

    createProcessesTable() {
        return `
            <div class="karasu-card">
                <div class="card-header">
                    <h3><i class="fas fa-tasks"></i> Активные процессы</h3>
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <select id="processLimit" style="padding: 6px 12px; background: var(--karasu-gray); border: 1px solid var(--karasu-border); border-radius: 4px; color: var(--karasu-text);">
                            <option value="10">10 процессов</option>
                            <option value="20">20 процессов</option>
                            <option value="50">50 процессов</option>
                        </select>
                        <button id="refreshProcesses" style="padding: 6px 12px; background: var(--karasu-gray); border: 1px solid var(--karasu-border); border-radius: 4px; color: var(--karasu-text); cursor: pointer;">
                            <i class="fas fa-redo"></i>
                        </button>
                    </div>
                </div>
                <div id="processesContainer" style="min-height: 300px;">
                    <!-- Процессы будут загружены здесь -->
                </div>
            </div>
        `;
    }
}

window.systemProcesses = new SystemProcesses();