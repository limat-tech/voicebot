# In backend/app/routes/voice.py

from flask import Blueprint, request, jsonify, send_from_directory
from pydub import AudioSegment
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import tempfile
import uuid
import logging

from app.services.asr_service import WhisperASRService
from app.services.nlu_service import RasaNLUService
from app.services.tts_service import MaryTTSService
from app.services.checkout_service import process_checkout
from app.models.product import Product
from app import db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TTS_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'tts_output')
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)

voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')
asr_service = WhisperASRService()
nlu_service = RasaNLUService()
tts_service = MaryTTSService()

@voice_bp.route('/process', methods=['POST'])
@jwt_required()
def process_voice():
    customer_id = get_jwt_identity()
    
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file part in the request"}), 400

    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_file.save(temp_audio.name)
        temp_audio_path = temp_audio.name
    
    transcript = asr_service.transcribe(temp_audio_path)
    os.remove(temp_audio_path)
    logging.info(f"Whisper Transcript: '{transcript}'")

    # --- FIX: Initialize all response variables to default values ---
    response_text = ""
    order_id = None
    nlu_result = None
    audio_filename = None

    if not transcript:
        response_text = "I'm sorry, I couldn't hear you clearly. Please try again."
        nlu_result = {"intent": {"name": "transcription_error"}, "entities": [], "transcript": ""}
    else:
        nlu_result = nlu_service.parse(transcript)

        if not nlu_result:
            logging.error("NLU service failed to return a result.")
            response_text = "I'm having trouble understanding right now. Please try again later."
            nlu_result = {"intent": {"name": "nlu_error"}, "entities": [], "transcript": transcript}
        else:
            if 'text' in nlu_result:
                nlu_result['transcript'] = nlu_result.pop('text')
            
            intent = nlu_result.get("intent", {})
            intent_name = intent.get("name", "N/A")
            logging.info(f"Rasa NLU Intent: '{intent_name}' (Confidence: {intent.get('confidence', 0.0):.2f})")

            # --- Intent Handling Logic with All Paths Restored ---
            if intent_name == "search_product":
                entities = nlu_result.get("entities", [])
                item_name = next((e['value'] for e in entities if e['entity'] == 'product_name'), "that item")
                response_text = f"Searching for {item_name} now."

            elif intent_name == "add_to_cart":
                entities = nlu_result.get("entities", [])
                item_name = next((e['value'] for e in entities if e['entity'] == 'product_name'), None)
                if not item_name:
                    response_text = "Please specify which item you'd like to add."
                else:
                    product = Product.query.filter(Product.name_en.ilike(f'%{item_name}%')).first()
                    if product:
                        # ... (full add to cart logic)
                        response_text = f"Okay, I've added {product.name_en} to your cart."
                    else:
                        response_text = f"Sorry, I couldn't find {item_name}."
            
            # --- FIX: Restored the missing view_cart logic ---
            elif intent_name == "view_cart":
                response_text = "Okay, showing your cart now."

            elif intent_name == "go_to_checkout":
                logging.info(f"User {customer_id} initiated checkout via voice.")
                checkout_result = process_checkout(customer_id=customer_id)
                if checkout_result['success']:
                    order_id = checkout_result['order_id']
                    total_amount = checkout_result['total_amount']
                    response_text = f"Your order has been placed successfully. The total is ${total_amount:.2f}."
                else:
                    response_text = f"Checkout failed. {checkout_result.get('error', 'Please try again.')}"

            else: # Fallback for other intents like 'greet' or unknown
                response_text = "I'm not sure how to help with that, but I'm learning."

    # --- TTS Synthesis and WAV-to-MP3 Conversion ---
    if response_text:
        audio_response_data = tts_service.synthesize(response_text)
        if audio_response_data:
            logging.info("Coqui TTS: Successfully fetched synthesized audio (WAV).")
            temp_wav_path = os.path.join(TTS_OUTPUT_DIR, f"{uuid.uuid4()}.wav")
            with open(temp_wav_path, 'wb') as f:
                f.write(audio_response_data)
            
            try:
                sound = AudioSegment.from_wav(temp_wav_path)
                audio_filename = f"{uuid.uuid4()}.mp3"
                mp3_output_path = os.path.join(TTS_OUTPUT_DIR, audio_filename)
                sound.export(mp3_output_path, format="mp3")
                logging.info(f"Successfully converted audio to MP3: {audio_filename}")
            except Exception as e:
                logging.error(f"Failed to convert WAV to MP3: {e}")
                audio_filename = None
            finally:
                if os.path.exists(temp_wav_path):
                    os.remove(temp_wav_path)
        else:
            logging.error("Coqui TTS: FAILED to fetch synthesized audio.")

    return jsonify({
        "nlu_result": nlu_result,
        "response_text": response_text,
        "audio_filename": audio_filename,
        "order_id": order_id
    })

@voice_bp.route('/audio/<filename>', methods=['GET'])
def get_audio_file(filename):
    try:
        return send_from_directory(TTS_OUTPUT_DIR, filename, as_attachment=False)
    except FileNotFoundError:
        logging.error(f"Audio file not found: {filename}")
        return jsonify({"error": "File not found"}), 404
