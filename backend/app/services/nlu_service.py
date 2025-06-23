# In app/services/nlu_service.py
import requests
from typing import Union, Dict

class RasaNLUService:
    """
    A service class to interact with a running Rasa NLU server.
    """
    def __init__(self, rasa_server_url="http://localhost:5005/model/parse"):
        """
        Initializes the service with the Rasa server's parsing endpoint.
        """
        self.url = rasa_server_url

    def parse(self, text: str, model: str = "nlu-en") -> Union[Dict, None]:
        """
        Sends text to the Rasa NLU server for intent and entity extraction.

        Args:
            text (str): The user's text to be parsed.
            model (str): The name of the Rasa model to use (e.g., 'nlu-en' or 'nlu-ar').

        Returns:
            dict: A dictionary containing the parsed data (intent, entities, confidence).
            None: If there was an error communicating with the Rasa server.
        """
        if not text:
            return None
        
        # The payload now includes the 'model' key to specify which NLU model to use.
        payload = {"text": text, "model": model}
        
        try:
            # Use json=payload to automatically handle content-type headers.
            response = requests.post(self.url, json=payload)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # Proper logging is important for debugging issues with the Rasa server.
            print(f"Error communicating with Rasa NLU server: {e}")
            return None
