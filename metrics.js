// Компонент для работы с метриками системы
class SystemMetrics {
    constructor() {
        this.chart = null;
        this.metricsHistory = [];
        this.maxHistory = 20;
    }

    async updateMetricsDisplay() {
        const metrics = await window.pythonAPI.getSystemMetrics();
        if (metrics) {
            this.updateMetricCards(metrics);
            this.updateChart(metrics);
            return metrics;
        }
        return null;
    }

    updateMetricCards(metrics) {
        // CPU
        const cpuElement = document.getElementById('cpuMetric');
        if (cpuElement) {
            cpuElement.textContent = `${Math.round(metrics.cpu.percent)}%`;
            this.updateProgressBar('cpuProgress', metrics.cpu.percent);
        }

        // RAM
        const ramElement = document.getElementById('ramMetric');
        if (ramElement) {
            ramElement.textContent = `${Math.round(metrics.ram.percent)}%`;
            this.updateProgressBar('ramProgress', metrics.ram.percent);
        }

        // Disk
        const diskElement = document.getElementById('diskMetric');
        if (diskElement) {
            diskElement.textContent = `${Math.round(metrics.disk.percent)}%`;
            this.updateProgressBar('diskProgress', metrics.disk.percent);
        }

        // Processes
        const processElement = document.getElementById('processMetric');
        if (processElement) {
            processElement.textContent = metrics.processes;
        }
    }

    updateProgressBar(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.width = `${value}%`;
            
            // Меняем цвет в зависимости от значения
            if (value > 80) {
                element.style.background = 'var(--karasu-error)';
            } else if (value > 60) {
                element.style.background = 'var(--karasu-warning)';
            } else {
                element.style.background = 'var(--karasu-success)';
            }
        }
    }

    createChart(canvasId) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array.from({length: this.maxHistory}, (_, i) => `${i}s`),
                datasets: [
                    {
                        label: 'CPU %',
                        data: Array(this.maxHistory).fill(0),
                        borderColor: '#e63946',
                        backgroundColor: 'rgba(230, 57, 70, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'RAM %',
                        data: Array(this.maxHistory).fill(0),
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#f5f5f5',
                            font: { family: "'Inter', sans-serif" }
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(17, 17, 17, 0.9)',
                        titleColor: '#f5f5f5',
                        bodyColor: '#f5f5f5',
                        borderColor: '#e63946',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#b1b1b1' }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#b1b1b1' }
                    }
                }
            }
        });

        return this.chart;
    }

    updateChart(metrics) {
        if (!this.chart) return;

        // Добавляем новые данные в историю
        this.metricsHistory.push({
            cpu: metrics.cpu.percent,
            ram: metrics.ram.percent,
            timestamp: new Date().toLocaleTimeString()
        });

        // Ограничиваем историю
        if (this.metricsHistory.length > this.maxHistory) {
            this.metricsHistory.shift();
        }

        // Обновляем график
        this.chart.data.datasets[0].data = this.metricsHistory.map(m => m.cpu);
        this.chart.data.datasets[1].data = this.metricsHistory.map(m => m.ram);
        this.chart.data.labels = this.metricsHistory.map(m => 
            new Date().toLocaleTimeString().slice(0, 5)
        );

        this.chart.update('none');
    }

    createMetricCard(title, value, icon, color = '#3498db') {
        return `
            <div class="karasu-card metric-card">
                <div class="metric-header">
                    <span class="metric-icon">${icon}</span>
                    <span class="metric-title">${title}</span>
                </div>
                <div class="metric-value" style="color: ${color}">${value}</div>
                <div class="metric-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 0%; background: ${color}"></div>
                    </div>
                </div>
            </div>
        `;
    }
}

window.systemMetrics = new SystemMetrics();