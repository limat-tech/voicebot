# app/routes/voice.py
from flask import Blueprint, request, jsonify, Response 
from app.services.asr_service import WhisperASRService
from app.services.nlu_service import RasaNLUService
from app.services.tts_service import MaryTTSService 
import os
import tempfile
import sys # Import the sys module

voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')

# --- Service Initialization ---
print("Initializing AI services for the voice blueprint...")
asr_service = WhisperASRService()
nlu_service = RasaNLUService()
tts_service = MaryTTSService() 
print("AI services initialized.")

@voice_bp.route('/process', methods=['POST'])
def process_voice():
    # --- Step 1: Receive and Save Audio ---
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file part in the request"}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No selected audio file"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_file.save(temp_audio.name)
        temp_audio_path = temp_audio.name

    transcript = None
    nlu_result = None
    
    try:
        # --- Step 2: ASR & NLU Processing ---
        transcript = asr_service.transcribe(temp_audio_path)
        
        # --- ADD THIS LINE TO SEE THE TRANSCRIPT ---
        print(f"--- Whisper Transcript: {transcript}", file=sys.stderr)
        
        if transcript:
            nlu_result = nlu_service.parse(transcript)
            
            # --- ADD THIS LINE TO SEE THE NLU RESULT ---
            print(f"--- Rasa NLU Result: {nlu_result}", file=sys.stderr)

    finally:
        # --- Step 3: Cleanup ---
        os.remove(temp_audio_path)

    if not transcript or not nlu_result:
        error_text = "I'm sorry, I had trouble understanding. Please try again."
        audio_response = tts_service.synthesize(error_text)
        if audio_response:
            return Response(audio_response, mimetype='audio/wav')
        else:
            return jsonify({"error": "Failed to process audio and could not generate TTS error"}), 500

    # --- Step 4: Intent Handling & Response Generation ---
    intent = nlu_result.get("intent", {}).get("name")
    response_text = ""

    if intent == "search_product":
        entities = nlu_result.get("entities", [])
        item_name = next((e['value'] for e in entities if e['entity'] == 'product_name'), "that item")
        response_text = f"Searching for {item_name} now."
    elif intent == "add_to_cart":
        response_text = "Item added to your cart."
    elif intent == "greet":
        response_text = "Hello! How can I help you with your shopping list today?"
    else:
        # This is the fallback response you are hearing
        response_text = "I'm not sure how to help with that, but I'm learning."

    # --- Step 5: TTS - Synthesize Audio from Text ---
    audio_response_data = tts_service.synthesize(response_text)

    if audio_response_data is None:
        return jsonify({"error": "Failed to synthesize audio response"}), 500

    # --- Step 6: Return Audio Response ---
    return Response(audio_response_data, mimetype='audio/wav')
