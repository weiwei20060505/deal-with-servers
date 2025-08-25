document.addEventListener('DOMContentLoaded', () => {
    // --- DOM 元素 ---
    const hostDropZone = document.getElementById('host-drop-zone');
    const commandDropZone = document.getElementById('command-drop-zone');
    const serverNameInput = document.getElementById('server-name');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const commandsTextarea = document.getElementById('commands-textarea');
    const hostFilenameDisplay = document.getElementById('host-filename');
    const commandFilenameDisplay = document.getElementById('command-filename');
    const executeBtn = document.getElementById('execute-btn');

    // --- 用變數來儲存 host.txt 的原始文字內容 ---
    let hostFileContent = '';
    
    // --- 建立結果顯示區塊 ---
    const outputDisplay = document.createElement('pre');
    outputDisplay.style.backgroundColor = '#222';
    outputDisplay.style.color = '#eee';
    outputDisplay.style.padding = '15px';
    outputDisplay.style.borderRadius = '8px';
    outputDisplay.style.marginTop = '20px';
    outputDisplay.style.whiteSpace = 'pre-wrap';
    outputDisplay.style.wordBreak = 'break-all';
    outputDisplay.textContent = '執行結果將顯示在這裡...';
    document.querySelector('.execute-section').appendChild(outputDisplay);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // --- 拖放區塊的通用設定 ---
    const setupDropZone = (dropZone, expectedFilename, filenameDisplay, fileHandler) => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });
        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            const targetFile = Array.from(files).find(file => file.name === expectedFilename);
            if (targetFile) {
                filenameDisplay.textContent = `Loaded: ${targetFile.name}`;
                fileHandler(targetFile);
            } else {
                const originalText = filenameDisplay.textContent;
                filenameDisplay.textContent = `Error: Please drop ${expectedFilename}.`;
                setTimeout(() => {
                    if (filenameDisplay.textContent.startsWith('Error:')) {
                        filenameDisplay.textContent = originalText.startsWith('Loaded:') ? originalText : '';
                    }
                }, 3000);
            }
        }, false);
    };

    // --- 設定 Host 拖放區：讀取原始文字 ---
    const handleHostFile = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            hostFileContent = e.target.result;
            hostFilenameDisplay.textContent = `已載入 host.txt 的內容。`;
        };
        reader.onerror = () => {
            hostFilenameDisplay.textContent = '錯誤：無法讀取 host.txt。';
        };
        reader.readAsText(file);
    };
    setupDropZone(hostDropZone, 'host.txt', hostFilenameDisplay, handleHostFile);

    // --- 設定 Command 拖放區：讀取原始文字 ---
    const handleCommandFile = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            commandsTextarea.value = e.target.result;
        };
        reader.onerror = () => {
            commandFilenameDisplay.textContent = '錯誤：無法讀取 command.txt。';
        };
        reader.readAsText(file);
    };
    setupDropZone(commandDropZone, 'command.txt', commandFilenameDisplay, handleCommandFile);

    // --- 【已升級】設定 Execute 按鈕的點擊事件 ---
    executeBtn.addEventListener('click', async () => {
        const commandContent = commandsTextarea.value;
        let combinedHostData = hostFileContent.trim(); // 從檔案內容開始

        // 檢查手動輸入欄位
        const manualServerName = serverNameInput.value.trim();
        const manualUsername = usernameInput.value.trim();
        const manualPassword = passwordInput.value.trim();

        // 如果手動輸入了伺服器名稱，就將其附加到 host 資料中
        if (manualServerName) {
            const manualEntry = `${manualServerName},${manualUsername},${manualPassword}`;
            if (combinedHostData) {
                // 如果已有檔案內容，就用換行符號隔開
                combinedHostData += '\n' + manualEntry;
            } else {
                // 如果沒有檔案內容，就直接使用手動輸入的資料
                combinedHostData = manualEntry;
            }
        }

        // 資料驗證
        if (!combinedHostData) {
            alert('請拖放 host.txt 檔案或手動填寫伺服器資訊！');
            return;
        }
        if (!commandContent) {
            alert('請拖放 command.txt 檔案或在文字區塊中輸入指令！');
            return;
        }

        // 準備 payload，包含合併後的 host 資料和指令資料
        const payload = {
            host_data: combinedHostData,
            command_data: commandContent
        };

        // ... 後續的 fetch 邏輯不變 ...
        executeBtn.disabled = true;
        executeBtn.textContent = '執行中...';
        outputDisplay.textContent = '正在將資料傳送到後端...';

        try {
            const response = await fetch('http://127.0.0.1:5000/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            
            if (result.status === 'error' || result.status === 'partial_success') {
                outputDisplay.style.color = '#ffb8b8';
            } else {
                outputDisplay.style.color = '#b8ffb8';
            }
            outputDisplay.textContent = result.output || JSON.stringify(result, null, 2);

        } catch (error) {
            console.error('連線到後端時發生錯誤：', error);
            outputDisplay.style.color = '#ffb8b8';
            outputDisplay.textContent = '錯誤：無法連線到後端伺服器。請確認伺服器已啟動。';
        } finally {
            executeBtn.disabled = false;
            executeBtn.textContent = 'Execute';
        }
    });
});
