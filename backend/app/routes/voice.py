# In backend/app/routes/voice.py

from flask import Blueprint, request, jsonify, send_from_directory
from pydub import AudioSegment
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import tempfile
import uuid
import logging

# --- Project-specific imports ---
from app.services.language_service import detect_language
from app.services.asr_service import WhisperASRService
from app.services.nlu_service import RasaNLUService
from app.services.tts_service import CoquiTTSService
from app.services.checkout_service import process_checkout
from app.models.product import Product
from app.models.shopping_cart import ShoppingCart
from app.models.cart_item import CartItem
from app import db

# --- Initial Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TTS_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'tts_output')
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)

# --- Blueprint and Service Instantiation ---
voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')
asr_service = WhisperASRService()
nlu_service = RasaNLUService()
tts_service = CoquiTTSService()

# This dictionary maps a language code to the chosen speaker ID.
# 'Ana Florence' is a high-quality English voice.
# 'Suad Qasim' is the corresponding high-quality Arabic voice.
SPEAKER_MAP = {
    "en": "Ana Florence",
    "ar": "Suad Qasim"
}

# --- Helper function for shared dialogue logic ---
def _handle_dialogue_logic(transcript, customer_id):
    """
    Handles NLU parsing, intent logic, and response generation.
    """
    response_text = ""
    order_id = None
    language = "en"  # Default language

    if not transcript:
        response_text = "I'm sorry, I couldn't hear you clearly. Please try again."
        nlu_result = {"intent": {"name": "transcription_error"}, "entities": [], "transcript": ""}
    else:
        language = detect_language(transcript)
        logging.info(f"Detected language: '{language}'.")

        nlu_result = nlu_service.parse(transcript, language=language)

        if not nlu_result or "error" in nlu_result:
            logging.error("NLU service failed or returned an error.")
            response_text = "I'm having trouble understanding right now. Please try again later."
            nlu_result = {"intent": {"name": "nlu_error"}, "entities": [], "transcript": transcript}
        else:
            if 'text' in nlu_result:
                nlu_result['transcript'] = nlu_result.pop('text')
            
            intent = nlu_result.get("intent", {})
            intent_name = intent.get("name", "N/A")
            logging.info(f"Rasa NLU Intent: '{intent_name}' (Confidence: {intent.get('confidence', 0.0):.2f})")

            # --- Bilingual Intent Handling Logic ---
            if intent_name == "search_product":
                entities = nlu_result.get("entities", [])
                item_name = next((e['value'] for e in entities if e['entity'] == 'product_name'), None)
                if language == 'ar':
                    response_text = f"جاري البحث عن {item_name}." if item_name else "عذراً، عن أي منتج تبحث؟"
                else:
                    response_text = f"Searching for {item_name}." if item_name else "Sorry, what product are you looking for?"

            elif intent_name == "add_to_cart":
                logging.info(f"Handling 'add_to_cart' intent for customer {customer_id}")
                entities = nlu_result.get("entities", [])
                item_name = next((e['value'] for e in entities if e['entity'] == 'product_name'), None)

                if not item_name:
                    # If the user just says "add to cart" without specifying an item
                    response_text = "الرجاء تحديد المنتج الذي ترغب في إضافته." if language == 'ar' else "Please specify which item you'd like to add."
                else:
                    # Find the product in the database using the extracted name
                    if language == 'ar':
                        product_query = Product.query.filter(Product.name_ar.ilike(f'%{item_name}%'))
                    else:
                        product_query = Product.query.filter(Product.name_en.ilike(f'%{item_name}%'))
                    
                    product = product_query.first()

                    if product:
                        # Find or create the user's cart
                        cart = ShoppingCart.query.filter_by(customer_id=customer_id).first()
                        if not cart:
                            cart = ShoppingCart(customer_id=customer_id)
                            db.session.add(cart)
                        
                        # Check if the item is already in the cart
                        cart_item = CartItem.query.filter_by(cart_id=cart.cart_id, product_id=product.product_id).first()
                        if cart_item:
                            cart_item.quantity += 1  # Increment quantity
                        else:
                            cart_item = CartItem(cart_id=cart.cart_id, product_id=product.product_id, quantity=1)
                            db.session.add(cart_item)
                        
                        db.session.commit()
                        
                        # Generate confirmation response
                        product_display_name = product.name_ar if language == 'ar' else product.name_en
                        if language == 'ar':
                            response_text = f"تمام، لقد أضفت {product_display_name} إلى سلتك."
                        else:
                            response_text = f"Okay, I've added {product_display_name} to your cart."
                    else:
                        # Product not found
                        if language == 'ar':
                            response_text = f"عذراً، لم أجد منتجاً باسم '{item_name}'."
                        else:
                            response_text = f"Sorry, I couldn't find an item named '{item_name}'."
            
            elif intent_name == "go_to_checkout":
                logging.info(f"User {customer_id} initiated checkout via voice.")
                checkout_result = process_checkout(customer_id=customer_id)
                if checkout_result['success']:
                    order_id = checkout_result['order_id']
                    total_amount = checkout_result['total_amount']
                    if language == 'ar':
                        response_text = f"تم تأكيد طلبك بنجاح. المبلغ الإجمالي هو {total_amount:.2f} درهم."
                    else:
                        response_text = f"Your order has been placed successfully. The total is AED {total_amount:.2f}."
                else:
                    error_msg = checkout_result.get('error', 'Please try again.')
                    response_text = f"فشلت عملية الدفع. {error_msg}" if language == 'ar' else f"Checkout failed. {error_msg}"

            else: # Fallback for 'greet', 'goodbye', or unknown intents
                if language == 'ar':
                    response_text = "أهلاً بك! كيف يمكنني مساعدتك اليوم؟"
                else:
                    response_text = "Hello! How can I help you today?"

    return response_text, nlu_result, order_id, language

# --- Main Production Route (Handles Audio Files) ---
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

    response_text, nlu_result, order_id, language = _handle_dialogue_logic(transcript, customer_id)

    audio_filename = None
    if response_text:
        # Select the speaker ID based on the detected language, defaulting to English
        speaker_id = SPEAKER_MAP.get(language, SPEAKER_MAP["en"])
        
        # Call the TTS service with the correct speaker ID
        audio_response_data = tts_service.synthesize(response_text, language=language, speaker_idx=speaker_id)
        
        if audio_response_data:
            temp_wav_path = os.path.join(TTS_OUTPUT_DIR, f"{uuid.uuid4()}.wav")
            with open(temp_wav_path, 'wb') as f: f.write(audio_response_data)
            try:
                sound = AudioSegment.from_wav(temp_wav_path)
                audio_filename = f"{uuid.uuid4()}.mp3"
                mp3_output_path = os.path.join(TTS_OUTPUT_DIR, audio_filename)
                sound.export(mp3_output_path, format="mp3")
                logging.info(f"Successfully converted audio to MP3: {audio_filename}")
            except Exception as e:
                logging.error(f"Failed to convert WAV to MP3: {e}")
            finally:
                if os.path.exists(temp_wav_path): os.remove(temp_wav_path)

    return jsonify({
        "nlu_result": nlu_result,
        "response_text": response_text,
        "audio_filename": audio_filename,
        "order_id": order_id,
        "detected_language": language
    })

# --- Temporary Testing Route (Handles JSON Text) ---
@voice_bp.route('/process-text', methods=['POST'])
@jwt_required()
def process_text_for_testing():
    customer_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'transcript' not in data:
        return jsonify({"error": "Request must be JSON with a 'transcript' field"}), 400

    transcript = data.get('transcript')
    logging.info(f"Received Text for Processing: '{transcript}'")
    
    response_text, nlu_result, order_id, language = _handle_dialogue_logic(transcript, customer_id)
    
    audio_filename = None
    if response_text:
        # Select the speaker ID based on the detected language, defaulting to English
        speaker_id = SPEAKER_MAP.get(language, SPEAKER_MAP["en"])

        # Call the TTS service with the correct speaker ID
        audio_response_data = tts_service.synthesize(response_text, language=language, speaker_idx=speaker_id)

        if audio_response_data:
            temp_wav_path = os.path.join(TTS_OUTPUT_DIR, f"{uuid.uuid4()}.wav")
            with open(temp_wav_path, 'wb') as f: f.write(audio_response_data)
            try:
                sound = AudioSegment.from_wav(temp_wav_path)
                audio_filename = f"{uuid.uuid4()}.mp3"
                mp3_output_path = os.path.join(TTS_OUTPUT_DIR, audio_filename)
                sound.export(mp3_output_path, format="mp3")
                logging.info(f"Successfully converted audio to MP3: {audio_filename}")
            except Exception as e:
                logging.error(f"Failed to convert WAV to MP3: {e}")
            finally:
                if os.path.exists(temp_wav_path): os.remove(temp_wav_path)

    return jsonify({
        "nlu_result": nlu_result,
        "response_text": response_text,
        "audio_filename": audio_filename,
        "order_id": order_id,
        "detected_language": language
    })

# --- Route to serve the generated audio files ---
@voice_bp.route('/audio/<filename>', methods=['GET'])
def get_audio_file(filename):
    """
    Serves the generated MP3 audio file to the frontend.
    """
    try:
        return send_from_directory(TTS_OUTPUT_DIR, filename, as_attachment=False)
    except FileNotFoundError:
        logging.error(f"Audio file not found: {filename}")
        return jsonify({"error": "File not found"}), 404
