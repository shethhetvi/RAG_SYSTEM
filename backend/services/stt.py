import os
import requests

def transcribe_audio(file_bytes: bytes) -> str:
    """
    Transcribes audio bytes using Sarvam API.
    Falls back to a mock transcription if API key is missing or call fails.
    """
    api_key = os.getenv("SARVAM_API_KEY")
    
    if not api_key or api_key == "your_sarvam_api_key_here":
        print("SARVAM_API_KEY not found or invalid. Using mock transcription.")
        return "This is a mock transcription because the Sarvam API key is missing."

    url = "https://api.sarvam.ai/speech-to-text-translate"
    
    headers = {
        "api-subscription-key": api_key
    }
    
    files = {
        'file': ('audio.wav', file_bytes, 'audio/wav')
    }
    
    data = {
        "prompt": ""
    }

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        return result.get("transcript", "Mock transcription: " + str(result))
    except Exception as e:
        print(f"STT Error: {e}")
        return f"Error during transcription: {e}"
