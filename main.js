const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess = null;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 700,
        frame: false,
        titleBarStyle: 'hidden',
        backgroundColor: '#0a0a0a',
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true
        }
    });

    mainWindow.loadFile('src/renderer/index.html');
    
    // Открываем DevTools в разработке
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }

    // Запускаем Python backend через 2 секунды
    setTimeout(() => {
        startPythonBackend();
    }, 2000);
}

function startPythonBackend() {
    try {
        const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
        const apiPath = path.join(__dirname, 'src', 'main', 'python_api.py');
        
        console.log('Запуск Python backend...');
        console.log('Python путь:', pythonPath);
        console.log('API путь:', apiPath);
        
        pythonProcess = spawn(pythonPath, [apiPath], {
            cwd: __dirname,
            stdio: ['pipe', 'pipe', 'pipe'],
            shell: true,
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
        });

        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString().trim();
            if (output) {
                console.log(`Python: ${output}`);
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            const error = data.toString().trim();
            if (error) {
                console.error(`Python ошибка: ${error}`);
            }
        });

        pythonProcess.on('close', (code) => {
            console.log(`Python процесс завершен с кодом: ${code}`);
            if (code !== 0 && code !== null) {
                console.log('Перезапуск Python через 5 секунд...');
                setTimeout(startPythonBackend, 5000);
            }
        });

        pythonProcess.on('error', (err) => {
            console.error('Не удалось запустить Python процесс:', err.message);
        });

        console.log('Python backend запущен');

    } catch (error) {
        console.error('Ошибка при запуске Python:', error.message);
    }
}

app.whenReady().then(() => {
    createWindow();
    
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (pythonProcess) {
        console.log('Остановка Python процесса...');
        pythonProcess.kill();
    }
    
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// IPC обработчики для управления окном
ipcMain.on('minimize-window', () => {
    if (mainWindow) {
        mainWindow.minimize();
    }
});

ipcMain.on('maximize-window', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow.maximize();
        }
    }
});

ipcMain.on('close-window', () => {
    if (mainWindow) {
        mainWindow.close();
    }
});

ipcMain.on('restart-python-backend', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
    startPythonBackend();
});

// Обработчик для проверки Python
ipcMain.handle('check-python-backend', async () => {
    try {
        const response = await fetch('http://localhost:5000/api/health');
        if (response.ok) {
            const data = await response.json();
            return {
                success: true,
                status: data.status,
                version: data.version
            };
        } else {
            return {
                success: false,
                error: 'Python backend не отвечает'
            };
        }
    } catch (error) {
        return {
            success: false,
            error: 'Не удалось подключиться к Python backend'
        };
    }
});