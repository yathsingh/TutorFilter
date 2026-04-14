// static/js/pipeline.js
const socket = io();
const micBtn = document.getElementById('mic-btn');
const statusText = document.getElementById('status');
const chatWindow = document.getElementById('chat-window');

// Initialize Browser Speech Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

if (recognition) {
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
} else {
    statusText.innerText = "⚠ Your browser does not support speech recognition. Use Chrome.";
}

let isAiTalking = false;
let finalTranscript = "";

// --- PUSH-TO-TALK LOGIC ---
micBtn.onmousedown = () => {
    if (isAiTalking || !recognition) return;
    
    finalTranscript = "";
    try {
        recognition.start();
        micBtn.classList.add('recording');
        statusText.innerText = "🎙️ Cue is listening... (Release to send)";
    } catch (e) {
        console.error("Recognition already started or failed:", e);
    }
};

micBtn.onmouseup = () => {
    if (!recognition) return;
    
    recognition.stop();
    micBtn.classList.remove('recording');
    statusText.innerText = "⏳ Processing your response...";
    micBtn.disabled = true; // Wait for AI to respond

    // Small delay to ensure the last speech chunk is captured
    setTimeout(() => {
        if (finalTranscript.trim()) {
            addMessage('Candidate', finalTranscript);
            socket.emit('candidate_speech', { text: finalTranscript });
        } else {
            resetMicState();
        }
    }, 500);
};

if (recognition) {
    recognition.onresult = (event) => {
        let interimTranscript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript;
            } else {
                interimTranscript += event.results[i][0].transcript;
            }
        }
        // Live feedback in the status bar
        statusText.innerText = `👂 Hearing: "${finalTranscript + interimTranscript}"`;
    };
}

// --- HANDLING AI RESPONSE ---
socket.on('ai_response', (data) => {
    isAiTalking = true;
    addMessage('Cue', data.text);

    if (data.audio) {
        const audio = new Audio("data:audio/mpeg;base64," + data.audio);
        statusText.innerText = "🔊 Cue is speaking...";
        audio.play();
        audio.onended = () => resetMicState();
    } else {
        resetMicState();
    }
});

function resetMicState() {
    isAiTalking = false;
    micBtn.disabled = false;
    micBtn.innerText = "🎙️ Hold to Speak";
    statusText.innerText = "✅ Ready for input.";
}

function addMessage(sender, text) {
    const div = document.createElement('div');
    div.className = `message message-${sender.toLowerCase()}`;
    div.innerHTML = `<span class="message-label">${sender}</span><p>${text}</p>`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}