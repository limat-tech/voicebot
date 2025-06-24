# In app/services/tts_service.py
import requests
import logging
from typing import Union

# The URL for the Coqui TTS server API endpoint
COQUI_TTS_URL = "http://localhost:5002/api/tts"

class CoquiTTSService:
    """A service to interact with a locally running Coqui TTS server."""

    def synthesize(self, text: str, language: str = "en", speaker_idx: str = None) -> Union[bytes, None]:
        """
        Sends text to the Coqui TTS server and returns the synthesized audio.

        Args:
            text (str): The text to synthesize.
            language (str): The language code ('en', 'ar', etc.).
            speaker_idx (str, optional): The speaker ID to use for synthesis. Defaults to None.

        Returns:
            bytes: The raw WAV audio data.
            None: If there was an error.
        """
        # Base parameters required by the XTTS model
        # Note: Using 'language_id' and 'speaker_id' (not 'language_idx' and 'speaker_idx')
        params = {
            "text": text,
            "language_id": language,  # Changed from 'language_idx' to 'language_id'
        }

        # Add the speaker_id to the request if it's provided
        if speaker_idx:
            params["speaker_id"] = speaker_idx  # Changed from 'speaker_idx' to 'speaker_id'
            logging.info(f"Requesting TTS with speaker: '{speaker_idx}'")
        else:
            logging.warning("No speaker_idx provided for TTS synthesis. The server might default or fail.")

        try:
            logging.info(f"Sending request to Coqui TTS for language '{language}'")
            response = requests.get(COQUI_TTS_URL, params=params)
            response.raise_for_status()
            logging.info("Coqui TTS successfully returned audio data.")
            return response.content
        except requests.exceptions.RequestException as e:
            logging.error(f"Error connecting to Coqui TTS server: {e}")
            logging.error(f"Response Body: {e.response.text if e.response else 'No response'}")
            return None
