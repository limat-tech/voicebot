# app/services/asr_service.py
import whisper
from typing import Union

class WhisperASRService:
    """
    A service class for handling audio transcription using OpenAI's Whisper.
    The model is loaded once upon initialization for better performance.
    """
    def __init__(self, model_size="base.en"):
        """
        Loads the specified Whisper model into memory when the service is created.
        """
        print(f"Initializing ASR Service and loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded and ready.")

    def transcribe(self, audio_file_path: str) -> Union[str, None]:
        """
        Transcribes the audio from a given file path.

        Args:
            audio_file_path (str): The path to the audio file to be transcribed.

        Returns:
            str: The transcribed text.
            None: If an error occurs during transcription.
        """
        try:
            result = self.model.transcribe(audio_file_path)
            return result["text"]
        except Exception as e:
            # In a real application, you would use a proper logger here
            print(f"Error during transcription: {e}")
            return None
