document.addEventListener('DOMContentLoaded', () => {
    // ---- Ambient Particles Generation ----
    const particlesContainer = document.getElementById('particles');
    const particleCount = 20;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Randomize properties
        const size = Math.random() * 5 + 2;
        const left = Math.random() * 100;
        const duration = Math.random() * 20 + 10;
        const delay = Math.random() * 10;
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${left}vw`;
        particle.style.animationDuration = `${duration}s`;
        particle.style.animationDelay = `-${delay}s`;
        
        particlesContainer.appendChild(particle);
    }

    // ---- Document "Feeding" Zone Logic ----
    const feederZone = document.getElementById('feederZone');
    const fileInput = document.getElementById('fileInput');
    const fedFilesContainer = document.getElementById('fedFiles');

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        feederZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        feederZone.addEventListener(eventName, () => {
            feederZone.classList.add('drag-active');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        feederZone.addEventListener(eventName, () => {
            feederZone.classList.remove('drag-active');
        }, false);
    });

    feederZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }, false);

    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        ([...files]).forEach(file => {
            const fileNode = document.createElement('div');
            fileNode.classList.add('data-node');
            
            // Extract extension or use generic
            const ext = file.name.split('.').pop() || 'DATA';
            
            fileNode.innerHTML = `
                <svg viewBox="0 0 24 24" width="16" height="16" stroke="var(--accent-amber)" stroke-width="2" fill="none">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span>${file.name}</span>
            `;
            fedFilesContainer.appendChild(fileNode);

            // Simulate "assimilation" message
            simulateEntityResponse(`I have ingested the data packet: ${file.name}. It is now part of my neural matrix.`);
        });
    }

    // ---- The Entity Chat Logic ----
    const queryInput = document.getElementById('queryInput');
    const sendBtn = document.getElementById('sendBtn');
    const messageContainer = document.getElementById('messageContainer');

    function appendMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender === 'user' ? 'user-message' : 'entity-message');
        
        if (sender === 'entity') {
            // Glitch effect wrapper
            msgDiv.innerHTML = `<span class="glitch-text">${text}</span>`;
        } else {
            msgDiv.textContent = text;
        }
        
        messageContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        // Find parent container to scroll
        const content = document.querySelector('.entity-content');
        content.scrollTop = content.scrollHeight;
    }

    function simulateEntityResponse(text) {
        // Typing indicator mockup (could be added)
        setTimeout(() => {
            appendMessage(text, 'entity');
        }, 800 + Math.random() * 1000);
    }

    function handleSend() {
        const query = queryInput.value.trim();
        if (!query) return;

        appendMessage(query, 'user');
        queryInput.value = '';

        // Mock response
        simulateEntityResponse(`Processing frequency for "${query}"... My current database is unlinked to the server. Awaiting backend synchronization.`);
    }

    sendBtn.addEventListener('click', handleSend);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });
});
