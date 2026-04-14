import os
from google import genai
from google.genai import types
from core.prompts import SYSTEM_BASE
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_gemini_response(history, stage_instruction):
    try:
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_BASE + "\n\nCURRENT GOAL: " + stage_instruction
        )
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=history,
            config=config
        )
        
        if response.text:
            return response.text.strip()
        return "I'm sorry, I missed that. Could you say it again?"
    except Exception as e:
        print(f"[!] Gemini Error: {e}")
        return "I'm having a bit of trouble connecting to my brain. One moment!"

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