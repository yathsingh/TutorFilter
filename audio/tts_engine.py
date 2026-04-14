import asyncio
import base64
import io
import edge_tts

VOICE = "en-US-AriaNeural" 

async def _generate_audio_bytes(text):
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = io.BytesIO()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])
    
    return audio_data.getvalue()

def generate_tts_base64(text):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        audio_bytes = loop.run_until_complete(_generate_audio_bytes(text))
        return base64.b64encode(audio_bytes).decode('utf-8')
    finally:
        loop.close()