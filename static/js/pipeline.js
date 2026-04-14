// static/js/pipeline.js
const socket = io();
const micBtn = document.getElementById('mic-btn');
const endBtn = document.getElementById('end-btn');
const statusText = document.getElementById('status');
const timerText = document.getElementById('timer');
const chatWindow = document.getElementById('chat-window');
const evalCard = document.getElementById('evaluation-result');
const evalDisplay = document.getElementById('eval-display');

let startTime;
let timerInterval;

function startTimer() {
    if (timerInterval) return;
    startTime = Date.now();
    timerInterval = setInterval(() => {
        const diff = Date.now() - startTime;
        const mins = Math.floor(diff / 60000).toString().padStart(2, '0');
        const secs = Math.floor((diff % 60000) / 1000).toString().padStart(2, '0');
        timerText.innerText = `${mins}:${secs}`;
    }, 1000);
}

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

if (recognition) {
    recognition.continuous = false; // Auto-stop on silence
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    micBtn.disabled = false;
    statusText.innerText = "✅ Ready. Click to speak.";
}

let isAiTalking = false;
let isRecording = false;
let finalTranscript = "";
let interimTranscript = ""; // FIX: Made this global so onend can access it!

// --- CLICK TO TALK (AUTO-DETECT END) ---
micBtn.onclick = () => {
    if (isAiTalking || !recognition || isRecording) return;
    
    startTimer();
    finalTranscript = "";
    interimTranscript = ""; // FIX: Reset on new recording
    isRecording = true;
    
    try {
        recognition.start();
        micBtn.classList.add('recording');
        micBtn.innerHTML = '<span class="icon">🔴</span><span class="text">Listening...</span>';
        statusText.innerText = "🎙️ Listening... Speak now.";
    } catch (e) { 
        console.error("Recognition error:", e);
        isRecording = false; 
    }
};

recognition.onresult = (event) => {
    interimTranscript = ""; // Reset local interim state for this chunk
    for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
        } else {
            interimTranscript += event.results[i][0].transcript;
        }
    }
    statusText.innerText = `👂 Hearing: "${finalTranscript + interimTranscript}"`;
};

recognition.onend = () => {
    if (!isRecording) return; 
    
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.disabled = true;
    micBtn.innerHTML = '<span class="icon">⏳</span><span class="text">Processing...</span>';
    statusText.innerText = "⏳ Sending to Cue...";

    // FIX: Combine both so nothing gets lost when the browser cuts off early!
    const fullText = (finalTranscript + " " + interimTranscript).trim();
    
    if (fullText.length > 0) {
        addMessage('Candidate', fullText);
        showTypingIndicator();
        socket.emit('candidate_speech', { text: fullText });
    } else {
        statusText.innerText = "⚠️ Didn't catch that. Click to try again.";
        setTimeout(resetMicState, 2000);
    }
};

// --- TYPING INDICATOR ---
let typingDiv = null;

function showTypingIndicator() {
    if (typingDiv) return;
    typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatWindow.appendChild(typingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeTypingIndicator() {
    if (typingDiv) {
        typingDiv.remove();
        typingDiv = null;
    }
}

// --- SERVER RESPONSES ---
socket.on('ai_response', (data) => {
    removeTypingIndicator();
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

endBtn.onclick = () => {
    statusText.innerText = "📈 Finalizing evaluation...";
    clearInterval(timerInterval);
    socket.emit('end_interview');
};

socket.on('evaluation_complete', (data) => {
    evalCard.classList.remove('hidden');
    evalDisplay.innerText = JSON.stringify(JSON.parse(data.result), null, 2);
    statusText.innerText = "✅ Interview Complete.";
});

function resetMicState() {
    isAiTalking = false;
    isRecording = false;
    micBtn.disabled = false;
    micBtn.classList.remove('recording');
    micBtn.innerHTML = '<span class="icon">🎙️</span><span class="text">Click to Speak</span>';
    statusText.innerText = "✅ Ready.";
}

function addMessage(sender, text) {
    const div = document.createElement('div');
    div.className = `message message-${sender.toLowerCase()}`;
    div.innerHTML = `<span class="message-label">${sender}</span><p>${text}</p>`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}