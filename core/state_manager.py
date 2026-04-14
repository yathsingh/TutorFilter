# core/state_manager.py
from core.prompts import SYSTEM_BASE, STAGES

class ConversationManager:
    def __init__(self):
        # Initialize with the base system prompt and the Intro stage
        self.history = [
            {"role": "user", "parts": [SYSTEM_BASE + "\n" + STAGES["INTRO"]]},
            {"role": "model", "parts": ["Understood. I am ready to begin the interview as Cue."]}
        ]
        self.turn_count = 0

    def add_message(self, role, text):
        self.history.append({"role": role, "parts": [text]})
        if role == "user":
            self.turn_count += 1

    def get_prompt_with_context(self, user_input):
        # Determine current stage based on the flow of conversation
        if self.turn_count < 2:
            current_goal = STAGES["INTRO"]
        elif self.turn_count < 5:
            current_goal = STAGES["PEDAGOGY"]
        else:
            current_goal = STAGES["CLOSING"]
        
        # We append the goal to the user's input so Gemini knows what to do next
        return f"{user_input}\n\n[System Note for Cue: {current_goal}]"

    def get_history(self):
        return self.history