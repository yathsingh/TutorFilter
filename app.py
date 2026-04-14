# app.py
import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from core.state_manager import ConversationManager
from core.gemini_client import get_gemini_response, evaluate_transcript
from audio.tts_engine import generate_tts_base64
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
active_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    active_sessions[request.sid] = ConversationManager()
    print(f"[+] New session: {request.sid}")

@socketio.on('candidate_speech')
def handle_speech(data):
    user_text = data.get('text', '').strip()
    session = active_sessions.get(request.sid)
    if not session or not user_text: return

    prompt = session.get_prompt_with_context(user_text)
    session.add_message("user", user_text)

    ai_text = get_gemini_response(session.get_history(), prompt)
    session.add_message("model", ai_text)

    audio_b64 = None
    try:
        audio_b64 = generate_tts_base64(ai_text)
    except Exception as e:
        print(f"[!] TTS Error: {e}")

    emit('ai_response', {'text': ai_text, 'audio': audio_b64})

@socketio.on('end_interview')
def handle_end():
    session = active_sessions.get(request.sid)
    if not session: return

    # Build transcript from memory
    transcript = ""
    for turn in session.get_history()[2:]:
        role = "Cue" if turn["role"] == "model" else "Candidate"
        transcript += f"{role}: {turn['parts'][0]['text']}\n\n"
    
    # Generate the JSON report
    report = evaluate_transcript(transcript)
    emit('evaluation_complete', {'result': report})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)