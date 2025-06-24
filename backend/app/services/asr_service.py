# app/services/asr_service.py
import whisper
from typing import Union, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

class WhisperASRService:
    """
    A service class for handling audio transcription using OpenAI's Whisper.
    Supports both English and Arabic with automatic language detection and forced language options.
    """
    
    def __init__(self, model_size="base"):
        """
        Loads the specified Whisper model into memory when the service is created.
        
        Args:
            model_size (str): The Whisper model to load. Use 'base' for multilingual support
                             instead of 'base.en' which is English-only.
        """
        logger.info(f"Initializing ASR Service and loading Whisper model: {model_size}")
        
        # Use multilingual model instead of English-only for Arabic support
        if model_size == "base.en":
            logger.warning("Switching from 'base.en' to 'base' for Arabic support")
            model_size = "base"
            
        self.model = whisper.load_model(model_size)
        logger.info("Whisper model loaded and ready for multilingual transcription.")

    def transcribe(self, audio_file_path: str, language: Optional[str] = None) -> Union[str, None]:
        """
        Transcribes the audio from a given file path with optional language specification.

        Args:
            audio_file_path (str): The path to the audio file to be transcribed.
            language (str, optional): Force a specific language ('en', 'ar', etc.). 
                                    If None, Whisper will auto-detect the language.

        Returns:
            str: The transcribed text.
            None: If an error occurs during transcription.
        """
        try:
            if language:
                # Force specific language (crucial for Arabic)
                logger.info(f"Transcribing with forced language: {language}")
                result = self.model.transcribe(audio_file_path, language=language)
            else:
                # Auto-detect language
                logger.info("Transcribing with auto-detection")
                result = self.model.transcribe(audio_file_path)
                detected_lang = result.get('language', 'unknown')
                logger.info(f"Auto-detected language: {detected_lang}")
                
                # If detected as English but might be Arabic, retry with Arabic
                if detected_lang == 'en' and self._might_be_arabic(result["text"]):
                    logger.info("Detected English but text appears to be Arabic, retrying with Arabic")
                    result = self.model.transcribe(audio_file_path, language='ar')
            
            transcribed_text = result["text"].strip()
            logger.info(f"Transcription successful: '{transcribed_text}'")
            return transcribed_text
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}", exc_info=True)
            return None

    def transcribe_with_detection(self, audio_file_path: str) -> dict:
        """
        Transcribes audio and returns both the text and detected language information.
        
        Args:
            audio_file_path (str): The path to the audio file to be transcribed.
            
        Returns:
            dict: Contains 'text', 'language', and 'confidence' if successful, 
                  or 'error' if transcription fails.
        """
        try:
            result = self.model.transcribe(audio_file_path)
            
            return {
                'text': result["text"].strip(),
                'language': result.get('language', 'unknown'),
                'confidence': result.get('language_probability', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error during transcription with detection: {e}", exc_info=True)
            return {'error': str(e)}

    def _might_be_arabic(self, text: str) -> bool:
        """
        Check if transcribed text might actually be Arabic that was misidentified as English.
        This helps catch cases where Arabic speech is transliterated to Latin characters.
        
        Args:
            text (str): The transcribed text to analyze.
            
        Returns:
            bool: True if the text might be Arabic, False otherwise.
        """
        # Common Arabic words that might be transliterated
        arabic_indicators = [
            'marhaba', 'marhaban',  # مرحبا (hello)
            'shukran',              # شكرا (thank you)
            'al-', 'el-',          # ال (the)
            'tuffah', 'tufah',     # تفاح (apple)
            'laban',               # لبن (milk)
            'khubz',               # خبز (bread)
            'basal',               # بصل (onion)
            'tamr',                # تمر (dates)
            'ruz',                 # رز (rice)
            'asal',                # عسل (honey)
            'ibn', 'bint',         # ابن، بنت (son, daughter)
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in arabic_indicators)

    def test_arabic_transcription(self, audio_file_path: str) -> dict:
        """
        Test method to compare auto-detection vs forced Arabic transcription.
        Useful for debugging Arabic transcription issues.
        
        Args:
            audio_file_path (str): The path to the audio file to test.
            
        Returns:
            dict: Comparison of auto-detected vs forced Arabic transcription.
        """
        try:
            # Auto-detect
            auto_result = self.model.transcribe(audio_file_path)
            
            # Force Arabic
            arabic_result = self.model.transcribe(audio_file_path, language='ar')
            
            # Force English for comparison
            english_result = self.model.transcribe(audio_file_path, language='en')
            
            return {
                'auto_detected': {
                    'text': auto_result['text'],
                    'language': auto_result.get('language', 'unknown'),
                    'confidence': auto_result.get('language_probability', 0.0)
                },
                'forced_arabic': {
                    'text': arabic_result['text']
                },
                'forced_english': {
                    'text': english_result['text']
                }
            }
            
        except Exception as e:
            logger.error(f"Error during test transcription: {e}", exc_info=True)
            return {'error': str(e)}