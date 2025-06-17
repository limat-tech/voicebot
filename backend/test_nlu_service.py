# test_nlu_service.py
from app.services.nlu_service import RasaNLUService
import pprint # Use pprint for nicely formatted dictionary output

# Create an instance of the service
nlu_service = RasaNLUService()

# Test phrase
test_text = "I need some bread"
print(f"--- Testing NLU Service with phrase: '{test_text}' ---")

# Call the parse method
result = nlu_service.parse(test_text)

if result:
    print("--- Received successful response from Rasa: ---")
    pprint.pprint(result)
else:
    print("--- Failed to get a response from the Rasa server. ---")
    print("Is the Rasa server running on port 5005?")
