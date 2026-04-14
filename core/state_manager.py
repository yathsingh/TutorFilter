from core.prompts import RECRUITER_SYSTEM_PROMPT

class ConversationManager:
    def __init__(self):
        self.history = [
            {"role": "user", "parts": [RECRUITER_SYSTEM_PROMPT]},
            {"role": "model", "parts": ["Understood. I am ready to begin the interview."]}
        ]
        self.turn_count = 0

    def add_user_message(self, text):
        self.history.append({"role": "user", "parts": [text]})
        self.turn_count += 1

    def add_model_message(self, text):
        self.history.append({"role": "model", "parts": [text]})

    def get_history(self):
        return self.history