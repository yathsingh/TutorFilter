from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from core.state_manager import ConversationManager
from core.gemini_client import get_chat_response, evaluate_candidate
from audio.tts_engine import get_tts_audio


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


active_sessions = {}


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    active_sessions[request.sid] = ConversationManager()
    print(f"Candidate connected: {request.sid}")


@socketio.on('candidate_speech')
def handle_speech(data):
    text = data.get('text')
    session_id = request.sid
    manager = active_sessions.get(session_id)

    if not manager or not text:
        return

    # 1. Save what the candidate said to memory
    manager.add_user_message(text)

    # 2. Ask Gemini what the Cuemath recruiter should reply
    ai_response_text = get_chat_response(manager.get_history())

    # 3. Save the recruiter's reply to memory
    manager.add_model_message(ai_response_text)

    # 4. Generate the audio waveform of the recruiter's reply
    audio_bytes = get_tts_audio(ai_response_text)

    # 5. Blast the text and the audio back down to the browser
    emit('ai_response', {
        'text': ai_response_text,
        'audio': audio_bytes
    })


@socketio.on('end_interview')
def handle_end_interview():
    session_id = request.sid
    manager = active_sessions.get(session_id)

    if manager:
        transcript_string = ""
        for turn in manager.get_history():
            if turn["role"] != "system":
                speaker = "Recruiter" if turn["role"] == "model" else "Candidate"
                transcript_string += f"{speaker}: {turn['parts'][0]}\n"


        evaluation_json = evaluate_candidate(transcript_string)


        emit('evaluation_complete', {'result': evaluation_json})


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)