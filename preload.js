const { contextBridge, ipcRenderer } = require('electron');

// Безопасно экспортируем API
contextBridge.exposeInMainWorld('electronAPI', {
    // Управление окном
    minimize: () => ipcRenderer.send('minimize-window'),
    maximize: () => ipcRenderer.send('maximize-window'),
    close: () => ipcRenderer.send('close-window'),
    
    // Взаимодействие с Python
    sendToPython: (channel, data) => {
        // Разрешаем только безопасные каналы
        const validChannels = [
            'command', 'speak', 'action', 
            'voice-start', 'voice-stop', 'ai-chat'
        ];
        
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    },
    
    // Получение данных
    onPythonResponse: (callback) => {
        // Фильтруем входящие данные
        ipcRenderer.on('python-response', (event, data) => {
            // Валидация данных
            if (typeof data === 'object' && data !== null) {
                callback(data);
            }
        });
    },
    
    // Файловая система (ограниченный доступ)
    selectFile: () => ipcRenderer.invoke('dialog:openFile'),
    selectFolder: () => ipcRenderer.invoke('dialog:openDirectory'),
    
    // Системные операции (требуют подтверждения)
    executeSystemAction: (action, params) => {
        return ipcRenderer.invoke('system:action', { action, params });
    }
});

// Защита от инъекций
process.once('loaded', () => {
    // Удаляем опасные глобальные объекты
    delete window.require;
    delete window.module;
    delete window.exports;
    delete window.global;
    
    // Защита от перезаписи API
    Object.freeze(window.electronAPI);
});