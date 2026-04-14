import edge_tts
import asyncio
import io


VOICE = "en-US-AriaNeural"


async def generate_audio_bytes(text):
    communicate = edge_tts.Communicate(text, VOICE)
    audio_data = io.BytesIO()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])
            
    return audio_data.getvalue()


def get_tts_audio(text):
    return asyncio.run(generate_audio_bytes(text))