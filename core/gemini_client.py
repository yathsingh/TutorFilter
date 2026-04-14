import os
import google.generativeai as genai
from core.prompts import EVALUATOR_SYSTEM_PROMPT


chat_model = genai.GenerativeModel('gemini-1.5-flash')
eval_model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config={"response_mime_type": "application/json"}
)


def get_chat_response(history):
    try:
        response = chat_model.generate_content(history)
        return response.text
    except Exception as e:
        print(f"Error generating chat response: {e}")
        return "I'm having a little trouble hearing you. Could you repeat that?"
    

def evaluate_candidate(transcript_text):
    try:
        evaluation_prompt = f"{EVALUATOR_SYSTEM_PROMPT}\n\nHere is the transcript:\n{transcript_text}"
        response = eval_model.generate_content(evaluation_prompt)
        return response.text
    except Exception as e:
        print(f"Error evaluating candidate: {e}")
        return '{"error": "Failed to generate evaluation."}'