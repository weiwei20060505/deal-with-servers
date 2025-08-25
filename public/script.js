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
    // 【新增】取得下載按鈕的元素
    const downloadBtn = document.getElementById('download-btn');

    // --- 全域變數 ---
    let hostFileContent = '';
    // 【新增】用一個變數來儲存最新的執行結果文字
    let latestResultText = '';

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

    // --- 拖放區塊的通用設定 (無變動) ---
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

    // --- 檔案處理函式 (無變動) ---
    const handleHostFile = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            hostFileContent = e.target.result;
            hostFilenameDisplay.textContent = `已載入 host.txt 的內容。`;
        };
        reader.readAsText(file);
    };
    setupDropZone(hostDropZone, 'host.txt', hostFilenameDisplay, handleHostFile);

    const handleCommandFile = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            commandsTextarea.value = e.target.result;
        };
        reader.readAsText(file);
    };
    setupDropZone(commandDropZone, 'command.txt', commandFilenameDisplay, handleCommandFile);

    // --- Execute 按鈕點擊事件 (微調) ---
    executeBtn.addEventListener('click', async () => {
        // ... (合併 host data 的邏輯不變)
        const commandContent = commandsTextarea.value;
        let combinedHostData = hostFileContent.trim();
        const manualServerName = serverNameInput.value.trim();
        if (manualServerName) {
            const manualEntry = `${manualServerName},${usernameInput.value.trim()},${passwordInput.value.trim()}`;
            combinedHostData = combinedHostData ? `${combinedHostData}\n${manualEntry}` : manualEntry;
        }

        if (!combinedHostData || !commandContent) {
            alert('請提供伺服器資訊和指令！');
            return;
        }

        const payload = {
            host_data: combinedHostData,
            command_data: commandContent
        };
        
        executeBtn.disabled = true;
        executeBtn.textContent = '執行中...';
        // 【修改】每次執行前，先隱藏下載按鈕並清空舊結果
        downloadBtn.classList.add('hidden');
        latestResultText = '';
        outputDisplay.textContent = '正在將資料傳送到後端...';

        try {
            const response = await fetch('http://127.0.0.1:5000/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            
            // 【修改】將結果存到全域變數中，並顯示下載按鈕
            latestResultText = result.output || '沒有收到任何輸出結果。';
            downloadBtn.classList.remove('hidden'); // 顯示按鈕

            if (result.status === 'error' || result.status === 'partial_success') {
                outputDisplay.style.color = '#ffb8b8';
            } else {
                outputDisplay.style.color = '#b8ffb8';
            }
            outputDisplay.textContent = latestResultText;

        } catch (error) {
            console.error('連線到後端時發生錯誤：', error);
            outputDisplay.style.color = '#ffb8b8';
            outputDisplay.textContent = '錯誤：無法連線到後端伺服器。請確認伺服器已啟動。';
        } finally {
            executeBtn.disabled = false;
            executeBtn.textContent = 'Execute';
        }
    });

    // --- 【新增】下載按鈕的點擊事件 ---
    downloadBtn.addEventListener('click', () => {
        if (!latestResultText) {
            alert('沒有可下載的結果！');
            return;
        }

        // 1. 建立一個 Blob 物件 (可以想像成一個虛擬的檔案)
        const blob = new Blob([latestResultText], { type: 'text/plain;charset=utf-8' });

        // 2. 建立一個隱藏的 <a> 連結元素
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob); // 將連結指向我們的虛擬檔案
        link.style.display = 'none';

        // 3. 設定下載的檔名
        const date = new Date();
        const timestamp = `${date.getFullYear()}${(date.getMonth()+1).toString().padStart(2, '0')}${date.getDate().toString().padStart(2, '0')}_${date.getHours().toString().padStart(2, '0')}${date.getMinutes().toString().padStart(2, '0')}`;
        link.download = `execution_log_${timestamp}.txt`;

        // 4. 將連結附加到網頁上，並模擬點擊它，然後移除
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});

