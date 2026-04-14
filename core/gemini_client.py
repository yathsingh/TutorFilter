# core/gemini_client.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_gemini_response(history, current_prompt):
    try:
        # Construct the conversation contents by appending the current prompt
        contents = history + [{"role": "user", "parts": [{"text": current_prompt}]}]
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=contents
        )
        
        if response.text:
            return response.text.strip()
        return "I'm sorry, could you repeat that?"
    except Exception as e:
        print(f"[!] Gemini Error: {e}")
        return "I'm having a bit of trouble connecting."

def evaluate_transcript(transcript_text):
    from core.prompts import EVALUATOR_PROMPT
    full_prompt = f"{EVALUATOR_PROMPT}\n\nTRANSCRIPT:\n{transcript_text}"
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_mime_type='application/json'
        )
    )
    return response.text