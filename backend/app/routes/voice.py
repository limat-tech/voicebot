from flask import Blueprint, request, jsonify

# Create a new Blueprint for voice-related routes
voice_bp = Blueprint('voice', __name__, url_prefix='/api/voice')

@voice_bp.route('/process', methods=['POST'])
def process_voice_command():
    # Get the transcribed text from the request body
    data = request.get_json()
    if not data or 'transcript' not in data:
        return jsonify({"error": "Missing transcript in request body"}), 400

    transcript = data['transcript'].lower()

    # --- This is where your mock logic from the plan goes ---
    if 'apple' in transcript:
        response_text = "I found 5 apple products. Would you like to add any to your cart?"
    elif 'milk' in transcript:
        response_text = "Here are the milk options available."
    else:
        response_text = "Sorry, I didn't understand that. Please try again."
    # --- End of mock logic ---

    # Return the response as defined in the plan
    return jsonify({
        "responseText": response_text,
        "audioUrl": None  # Placeholder for future TTS functionality
    })