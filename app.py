# app.py
import os
import base64
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from core.state_manager import ConversationManager
from core.gemini_client import get_gemini_response # You will build this in core/
from audio.tts_engine import generate_tts_base64 # You will build this in audio/
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Stores active interview sessions by Socket ID
active_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    # Start a fresh interview session when a user connects
    active_sessions[request.sid] = ConversationManager()
    print(f"[+] New session started: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    active_sessions.pop(request.sid, None)
    print(f"[-] Session ended: {request.sid}")

@socketio.on('candidate_speech')
def handle_speech(data):
    user_text = data.get('text', '').strip()
    session = active_sessions.get(request.sid)
    
    if not session or not user_text:
        return

    # 1. Update history and get dynamic prompt
    contextual_prompt = session.get_prompt_with_context(user_text)
    session.add_message("user", user_text)

    # 2. Get AI text response from Gemini
    ai_response_text = get_gemini_response(session.get_history(), contextual_prompt)
    session.add_message("model", ai_response_text)

    # 3. Convert text to speech (Base64)
    audio_b64 = None
    try:
        audio_b64 = generate_tts_base64(ai_response_text)
    except Exception as e:
        print(f"[!] TTS Error: {e}")

    # 4. Send everything back to the frontend
    emit('ai_response', {
        'text': ai_response_text,
        'audio': audio_b64
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)