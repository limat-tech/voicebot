# in app/services/tts_service.py
import requests

# This is the address where your MaryTTS server is listening.
MARY_TTS_URL = "http://localhost:59125/process"

class MaryTTSService:
    def synthesize(self, text: str, language: str = "en_US"):
        """
        Sends text to the MaryTTS server and returns the synthesized audio content.

        Args:
            text (str): The text to be converted to speech.
            language (str): The locale to use (e.g., "en_US").

        Returns:
            bytes: The raw audio data (.wav format) or None if an error occurs.
        """
        # These are the parameters MaryTTS expects in its API call.
        params = {
            "INPUT_TYPE": "TEXT",
            "OUTPUT_TYPE": "AUDIO",
            "AUDIO": "WAVE_FILE",
            "LOCALE": language,
            "INPUT_TEXT": text,
        }

        try:
            # We use the requests library to send an HTTP GET request.
            # The params dictionary is automatically converted into a URL query string.
            response = requests.get(MARY_TTS_URL, params=params, timeout=10)
            
            # This will raise an exception if the server returned an error (e.g., 404, 500).
            response.raise_for_status()
            
            # response.content contains the raw audio data as bytes.
            return response.content
        
        except requests.exceptions.RequestException as e:
            # This catches network errors, like if the MaryTTS server is not running.
            print(f"Error connecting to MaryTTS server: {e}")
            return None
