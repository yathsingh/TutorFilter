const socket = io();
const chatWindow = document.getElementById('chat-window');
const startBtn = document.getElementById('start-btn');
const endBtn = document.getElementById('end-btn');
const statusText = document.getElementById('status');


const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = false; 
recognition.lang = 'en-US';


startBtn.onclick = () => {
    recognition.start();
    startBtn.disabled = true;
    endBtn.disabled = false;
    statusText.innerText = "Listening...";
};


recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    addMessage('Candidate', transcript);
    socket.emit('candidate_speech', { text: transcript });
    statusText.innerText = "Processing...";
};


socket.on('ai_response', (data) => {
    addMessage('Recruiter', data.text);
    
    const blob = new Blob([data.audio], { type: 'audio/mpeg' });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
    
    audio.onended = () => {
        recognition.start();
        statusText.innerText = "Listening...";
    };
});


endBtn.onclick = () => {
    socket.emit('end_interview');
    statusText.innerText = "Generating Report...";
};

socket.on('evaluation_complete', (data) => {
    document.getElementById('evaluation-result').classList.remove('hidden');
    document.getElementById('json-display').innerText = JSON.stringify(JSON.parse(data.result), null, 2);
    statusText.innerText = "Interview Complete";
});


function addMessage(sender, text) {
    const div = document.createElement('div');
    div.className = sender.toLowerCase();
    div.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatWindow.appendChild(div);
}