# core/state_manager.py
from core.prompts import STAGES

class ConversationManager:
    def __init__(self):
        # History starts empty; system prompt is handled in the client
        self.history = []
        self.turn_count = 0

    def add_message(self, role, text):
        self.history.append({"role": role, "parts": [{"text": text}]})
        if role == "user":
            self.turn_count += 1

    def get_stage_instruction(self):
        # Determine current stage based on the flow
        if self.turn_count < 2:
            return STAGES["INTRO"]
        elif self.turn_count < 5:
            return STAGES["PEDAGOGY"]
        else:
            return STAGES["CLOSING"]

    def get_history(self):
        return self.history