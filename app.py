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
    print(f"[+] New session connected: {request.sid}")

@socketio.on('candidate_speech')
def handle_speech(data):
    user_text = data.get('text', '').strip()
    print(f"\n[DEBUG] 🎤 Received speech: '{user_text}'")
    
    session = active_sessions.get(request.sid)
    # Fallback: If SID changed due to polling reconnect, recover gracefully
    if not session: 
        print(f"[!] No session found for {request.sid}. Creating a new one.")
        session = ConversationManager()
        active_sessions[request.sid] = session

    if not user_text: 
        print("[!] Text was empty. Aborting AI generation.")
        return

    # 1. Add user message
    session.add_message("user", user_text)
    
    # 2. Get AI response
    print("[DEBUG] 🧠 Fetching Gemini response...")
    stage_note = session.get_stage_instruction()
    ai_text = get_gemini_response(session.get_history(), stage_note)
    print(f"[DEBUG] 🤖 Cue says: '{ai_text}'")
    
    # 3. Add AI response
    session.add_message("model", ai_text)

    # 4. Generate TTS
    audio_b64 = None
    try:
        print("[DEBUG] 🔊 Generating audio...")
        audio_b64 = generate_tts_base64(ai_text)
    except Exception as e:
        print(f"[!] TTS Error: {e}")

    emit('ai_response', {'text': ai_text, 'audio': audio_b64})
    print("[DEBUG] ✅ Response sent to frontend.")

@socketio.on('end_interview')
def handle_end():
    session = active_sessions.get(request.sid)
    if not session: return

    print("\n[DEBUG] 📈 Generating evaluation report...")
    transcript = ""
    for turn in session.get_history():
        role = "Cue" if turn["role"] == "model" else "Candidate"
        text = turn["parts"][0]["text"]
        transcript += f"{role}: {text}\n\n"
    
    report = evaluate_transcript(transcript)
    emit('evaluation_complete', {'result': report})
    print("[DEBUG] ✅ Report sent.")

if __name__ == '__main__':
    # Running on 0.0.0.0 ensures it binds correctly if your local network changes
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)