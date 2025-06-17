# app/services/nlu_service.py
import requests
import json
from typing import Union

class RasaNLUService:
    """
    A service class to interact with a running Rasa NLU server.
    """
    def __init__(self, rasa_server_url="http://localhost:5005/model/parse"):
        """
        Initializes the service with the Rasa server's parsing endpoint.
        """
        self.url = rasa_server_url

    def parse(self, text: str) -> Union[dict, None]:
        """
        Sends text to the Rasa NLU server for intent and entity extraction.

        Args:
            text (str): The user's text to be parsed.

        Returns:
            dict: A dictionary containing the parsed data (intent, entities, confidence).
            None: If there was an error communicating with the Rasa server.
        """
        if not text:
            return None
            
        payload = {"text": text}
        
        try:
            # Make the POST request to the Rasa server
            response = requests.post(self.url, data=json.dumps(payload))
            
            # Raise an exception if the request returned an error status code
            response.raise_for_status()
            
            # Return the JSON response as a Python dictionary
            return response.json()
            
        except requests.exceptions.RequestException as e:
            # In a real app, use a proper logger here
            print(f"Error communicating with Rasa NLU server: {e}")
            return None
