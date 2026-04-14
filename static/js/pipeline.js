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
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    micBtn.disabled = false;
    statusText.innerText = "✅ Ready for input.";
}

let isAiTalking = false;
let finalTranscript = "";

micBtn.onmousedown = () => {
    if (isAiTalking || !recognition) return;
    startTimer();
    finalTranscript = "";
    try {
        recognition.start();
        micBtn.classList.add('recording');
        statusText.innerText = "🎙️ Listening...";
    } catch (e) { console.error(e); }
};

micBtn.onmouseup = () => {
    if (!recognition) return;
    recognition.stop();
    micBtn.classList.remove('recording');
    statusText.innerText = "⏳ Processing...";
    micBtn.disabled = true;

    setTimeout(() => {
        if (finalTranscript.trim()) {
            addMessage('Candidate', finalTranscript);
            socket.emit('candidate_speech', { text: finalTranscript });
        } else { resetMicState(); }
    }, 500);
};

if (recognition) {
    recognition.onresult = (event) => {
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
            else interim += event.results[i][0].transcript;
        }
        statusText.innerText = `👂 Hearing: "${finalTranscript + interim}"`;
    };
}

socket.on('ai_response', (data) => {
    isAiTalking = true;
    addMessage('Cue', data.text);
    if (data.audio) {
        const audio = new Audio("data:audio/mpeg;base64," + data.audio);
        statusText.innerText = "🔊 Cue is speaking...";
        audio.play();
        audio.onended = () => resetMicState();
    } else { resetMicState(); }
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
    micBtn.disabled = false;
    micBtn.innerText = "🎙️ Hold to Speak";
    statusText.innerText = "✅ Ready.";
}

function addMessage(sender, text) {
    const div = document.createElement('div');
    div.className = `message message-${sender.toLowerCase()}`;
    div.innerHTML = `<span class="message-label">${sender}</span><p>${text}</p>`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}