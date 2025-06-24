# In app/services/nlu_service.py
import requests
import logging
from typing import Dict, Union

# Define the URLs for your two separate Rasa servers
RASA_SERVER_URLS = {
    "en": "http://localhost:5005/model/parse",
    "ar": "http://localhost:5006/model/parse",
}

class RasaNLUService:
    """
    A service class to interact with multiple running Rasa NLU servers,
    routing requests based on language.
    """
    def parse(self, text: str, language: str = "en") -> Union[Dict, None]:
        """
        Sends text to the appropriate Rasa NLU server based on language.

        Args:
            text (str): The user's text to be parsed.
            language (str): The detected language ('en' or 'ar'). This determines
                            which Rasa server to call.

        Returns:
            dict: A dictionary containing the parsed data from the correct model.
            None: If the language is unsupported or a server is down.
        """
        if language not in RASA_SERVER_URLS:
            logging.error(f"Unsupported language provided to NLU service: {language}")
            return None

        # Select the correct server URL based on the detected language
        target_url = RASA_SERVER_URLS[language]
        payload = {"text": text}
        
        try:
            logging.info(f"Sending NLU request for language '{language}' to {target_url}")
            response = requests.post(target_url, json=payload)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error communicating with Rasa NLU server at {target_url}: {e}")
            return {"error": f"NLU service for language '{language}' is unavailable."}

