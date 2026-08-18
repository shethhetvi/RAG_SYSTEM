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

    async function handleSend() {
        const query = queryInput.value.trim();
        if (!query) return;

        appendMessage(query, 'user');
        queryInput.value = '';

        try {
            const formData = new FormData();
            formData.append('query', query);

            const response = await fetch('http://localhost:8000/query/text', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            let reply = data.answer;
            if (data.timings) {
                reply += `\n\n[Latency - Total: ${(data.timings.total * 1000).toFixed(2)}ms]`;
            }
            simulateEntityResponse(reply);
        } catch (err) {
            simulateEntityResponse(`Connection error: ${err.message}`);
        }
    }

    sendBtn.addEventListener('click', handleSend);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });

    // ---- Voice Recording Logic ----
    const micBtn = document.getElementById('micBtn');
    let mediaRecorder;
    let audioChunks = [];

    micBtn.addEventListener('mousedown', async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                
                // Show analyzing state
                simulateEntityResponse('Analyzing audio frequency...');
                
                try {
                    const formData = new FormData();
                    formData.append('audio', audioBlob, 'voice.wav');

                    const response = await fetch('http://localhost:8000/query/audio', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    
                    let reply = `[Transcribed: "${data.query}"]\n\n${data.answer}`;
                    if (data.timings) {
                        reply += `\n\n[Latency - STT: ${(data.timings.stt * 1000).toFixed(2)}ms, Total: ${(data.timings.total * 1000).toFixed(2)}ms]`;
                    }
                    simulateEntityResponse(reply);
                } catch (err) {
                    simulateEntityResponse(`Audio Processing Error: ${err.message}`);
                }
            };

            mediaRecorder.start();
            micBtn.classList.add('recording');
        } catch (err) {
            alert('Microphone access denied or not available.');
        }
    });

    micBtn.addEventListener('mouseup', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            micBtn.classList.remove('recording');
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    });
    
    // Also stop on mouse leave in case user drags mouse off button
    micBtn.addEventListener('mouseleave', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            micBtn.classList.remove('recording');
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    });
});
