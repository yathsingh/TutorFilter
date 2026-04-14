# core/gemini_client.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Using the fast Flash model for low-latency voice interaction
chat_model = genai.GenerativeModel('gemini-2.0-flash')

def get_gemini_response(history, current_prompt):
    """
    Sends the conversation history and the current contextual 
    goal to Gemini to get Cue's next response.
    """
    try:
        # We append the 'System Note' to guide Cue's behavior 
        # without cluttering the long-term history.
        temp_history = history + [{"role": "user", "parts": [current_prompt]}]
        response = chat_model.generate_content(temp_history)
        
        if response.text:
            return response.text.strip()
        return "I'm sorry, could you repeat that?"
    except Exception as e:
        print(f"[!] Gemini Error: {e}")
        return "I'm having a bit of trouble connecting. Let's try again."

def evaluate_transcript(transcript_text):
    """
    Uses the Evaluator prompt to generate the structured JSON 
    report at the end of the 10 minutes.
    """
    from core.prompts import EVALUATOR_PROMPT
    
    # We use a specific model instance to ensure JSON output
    eval_model = genai.GenerativeModel(
        'gemini-2.0-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
    full_prompt = f"{EVALUATOR_PROMPT}\n\nTRANSCRIPT:\n{transcript_text}"
    response = eval_model.generate_content(full_prompt)
    return response.text