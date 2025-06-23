# In app/services/language_service.py
from langdetect import detect, LangDetectException

def detect_language(text: str) -> str:
    """
    Detects the language of a given text, prioritizing Arabic.
    Returns 'ar' for Arabic or 'en' for English/other as a fallback.
    """
    # This check for Arabic characters is more reliable for short, mixed, or ambiguous commands.
    if any('\u0600' <= char <= '\u06FF' for char in text):
        return 'ar'
    
    try:
        # Use the langdetect library for more comprehensive checks.
        lang = detect(text)
        return 'ar' if lang == 'ar' else 'en'
    except LangDetectException:
        # If detection fails (e.g., text is just numbers), default to English.
        return 'en'
