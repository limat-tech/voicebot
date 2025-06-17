# app/routes/voice.py
from flask import Blueprint, request, jsonify
from app.services.asr_service import WhisperASRService
from app.services.nlu_service import RasaNLUService
import os
import tempfile


voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')

# --- Industrial Practice: Service Initialization ---
# In a real production app, you would use a more robust way to ensure
# these services are created only once (e.g., using Flask's application factory pattern).
# For now, creating them when the blueprint is loaded is a great start.
print("Initializing AI services for the voice blueprint...")
asr_service = WhisperASRService()
nlu_service = RasaNLUService()
print("AI services initialized.")


@voice_bp.route('/process', methods=['POST'])
def process_voice():
    # Step 1: Check if an audio file was sent
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file part in the request"}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "No selected audio file"}), 400

    # Step 2: Save the audio to a temporary file
    # We use a temporary file because Whisper's transcribe function expects a file path.
    # 'delete=False' is important so we can close it and still use its path.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_file.save(temp_audio.name)
        temp_audio_path = temp_audio.name

    transcript = None
    nlu_result = None
    
    try:
        # --- Step 3: ASR - Transcribe audio to text ---
        transcript = asr_service.transcribe(temp_audio_path)
        
        # --- Step 4: NLU - Parse text for intent and entities ---
        if transcript:
            nlu_result = nlu_service.parse(transcript)

    finally:
        # --- Step 5: Cleanup - Always remove the temporary file ---
        os.remove(temp_audio_path)

    if not transcript or not nlu_result:
        return jsonify({"error": "Failed to process audio command"}), 500

    # Step 6: Return the full, structured result
    return jsonify({
        "transcript": transcript,
        "intent": nlu_result.get("intent", {}).get("name"),
        "entities": nlu_result.get("entities", []),
        "confidence": nlu_result.get("intent", {}).get("confidence")
    }), 200