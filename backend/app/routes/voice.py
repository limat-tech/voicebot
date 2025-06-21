# In backend/app/routes/voice.py

from flask import Blueprint, request, jsonify, send_from_directory
from app.services.asr_service import WhisperASRService
from app.services.nlu_service import RasaNLUService
from app.services.tts_service import MaryTTSService 
import os
import tempfile
import uuid
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity # <-- IMPORT JWT tools
from app.models.product import Product # <-- IMPORT Product model
from app.models.shopping_cart import ShoppingCart # <-- IMPORT ShoppingCart model
from app.models.cart_item import CartItem # <-- IMPORT CartItem model
from app import db # <-- IMPORT the database instance

# --- Existing Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TTS_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'tts_output')
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)

voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')

asr_service = WhisperASRService()
nlu_service = RasaNLUService()
tts_service = MaryTTSService() 

@voice_bp.route('/process', methods=['POST'])
@jwt_required() # <-- PROTECT THIS ENDPOINT so we know the user
def process_voice():
    # --- Step 1: Get Authenticated User ---
    # This is the user ID from the JWT token sent by the frontend.
    customer_id = get_jwt_identity()
    
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file part in the request"}), 400

    # ... (rest of the file upload and ASR logic is the same) ...
    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_file.save(temp_audio.name)
        temp_audio_path = temp_audio.name
    
    transcript = asr_service.transcribe(temp_audio_path)
    os.remove(temp_audio_path)
    logging.info(f"Whisper Transcript: '{transcript}'")

    if not transcript:
        # Handle transcription failure
        response_text = "I'm sorry, I couldn't hear you clearly. Please try again."
        nlu_result = {"intent": {"name": "transcription_error"}, "entities": []}
    else:
        # --- NLU and Intent Handling ---
        nlu_result = nlu_service.parse(transcript)
        intent = nlu_result.get("intent", {})
        intent_name = intent.get("name", "N/A")
        confidence = intent.get("confidence", 0.0)
        logging.info(f"Rasa NLU Intent: '{intent_name}' (Confidence: {confidence:.2f})")

        # --- REVISED INTENT LOGIC ---
        if intent_name == "search_product":
            entities = nlu_result.get("entities", [])
            item_name = next((e['value'] for e in entities if e['entity'] == 'product_name'), "that item")
            response_text = f"Searching for {item_name} now."

        elif intent_name == "add_to_cart":
            entities = nlu_result.get("entities", [])
            item_name = next((e['value'] for e in entities if e['entity'] == 'product_name'), None)
            
            if not item_name:
                response_text = "Please specify which item you'd like to add to the cart."
            else:
                # --- ACTUAL CART LOGIC ---
                product = Product.query.filter(Product.name_en.ilike(f'%{item_name}%')).first()
                if not product:
                    response_text = f"I'm sorry, I couldn't find {item_name} in our store."
                else:
                    # Find or create the user's shopping cart
                    cart = ShoppingCart.query.filter_by(customer_id=customer_id).first()
                    if not cart:
                        cart = ShoppingCart(customer_id=customer_id)
                        db.session.add(cart)
                    
                    # Check if item is already in cart
                    cart_item = CartItem.query.filter_by(cart_id=cart.cart_id, product_id=product.product_id).first()
                    if cart_item:
                        cart_item.quantity += 1
                    else:
                        cart_item = CartItem(cart_id=cart.cart_id, product_id=product.product_id, quantity=1)
                        db.session.add(cart_item)
                    
                    db.session.commit()
                    response_text = f"Okay, I've added {product.name_en} to your cart."
                    logging.info(f"Added product {product.product_id} to cart for customer {customer_id}")

        elif intent_name == "greet":
            response_text = "Hello! How can I help you with your shopping list today?"
        else:
            response_text = "I'm not sure how to help with that, but I'm learning."
    
    # --- TTS Step ---
    audio_response_data = tts_service.synthesize(response_text)
    audio_filename = None
    if audio_response_data:
        logging.info("Coqui TTS: Successfully fetched synthesized audio.")
        audio_filename = f"{uuid.uuid4()}.wav"
        with open(os.path.join(TTS_OUTPUT_DIR, audio_filename), 'wb') as f:
            f.write(audio_response_data)
    else:
        logging.error("Coqui TTS: FAILED to fetch synthesized audio.")

    return jsonify({
        "nlu_result": nlu_result,
        "response_text": response_text,
        "audio_filename": audio_filename
    })

# ... (the /audio/<filename> endpoint remains unchanged) ...
@voice_bp.route('/audio/<filename>', methods=['GET'])
def get_audio_file(filename):
    try:
        return send_from_directory(TTS_OUTPUT_DIR, filename, as_attachment=False)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
