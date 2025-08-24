document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const hostDropZone = document.getElementById('host-drop-zone');
    const commandDropZone = document.getElementById('command-drop-zone');
    const serverNameInput = document.getElementById('server-name');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const commandsTextarea = document.getElementById('commands-textarea');
    const hostFilenameDisplay = document.getElementById('host-filename');
    const commandFilenameDisplay = document.getElementById('command-filename');
    const executeBtn = document.getElementById('execute-btn');

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Reusable function to handle drag and drop events
    const setupDropZone = (dropZone, expectedFilename, filenameDisplay, fileHandler) => {
        // Prevent default drag behaviors on the entire page
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
        });

        // Handle dropped files
        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;

            // Find the expected file among potentially multiple dropped files
            const targetFile = Array.from(files).find(file => file.name === expectedFilename);

            if (targetFile) {
                filenameDisplay.textContent = `Loaded: ${targetFile.name}`;
                fileHandler(targetFile);
            } else {
                const originalText = filenameDisplay.textContent;
                filenameDisplay.textContent = `Error: Please drop ${expectedFilename}.`;
                // Clear the error message after 3 seconds
                setTimeout(() => {
                    // Only clear it if it's still the error message
                    if (filenameDisplay.textContent.startsWith('Error:')) {
                       filenameDisplay.textContent = originalText.startsWith('Loaded:') ? originalText : '';
                    }
                }, 3000);
            }
        }, false);
    };

    // --- Setup Host Drop Zone ---
    const handleHostFile = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const lines = e.target.result.split(/\\r\\n|\\n/); // Handles both Windows and Unix line endings
            if (lines.length >= 3) {
                serverNameInput.value = lines[0].trim();
                usernameInput.value = lines[1].trim();
                passwordInput.value = lines[2].trim();
            } else {
                hostFilenameDisplay.textContent = 'Error: host.txt is not formatted correctly.';
            }
        };
        reader.onerror = () => {
            hostFilenameDisplay.textContent = 'Error: Could not read file.';
        };
        reader.readAsText(file);
    };
    setupDropZone(hostDropZone, 'host.txt', hostFilenameDisplay, handleHostFile);

    // --- Setup Command Drop Zone ---
    const handleCommandFile = (file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            commandsTextarea.value = e.target.result;
        };
        reader.onerror = () => {
            commandFilenameDisplay.textContent = 'Error: Could not read file.';
        };
        reader.readAsText(file);
    };
    setupDropZone(commandDropZone, 'command.txt', commandFilenameDisplay, handleCommandFile);

    // --- Setup Execute Button ---
    executeBtn.addEventListener('click', () => {
        alert('Executing with provided details!');
    });
});
