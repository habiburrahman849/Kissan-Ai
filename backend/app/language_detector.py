def detect_language(message: str) -> str:
    """
    Detects if a message is written in English, Urdu (Arabic script), or Hinglish (Roman Urdu).
    Returns 'en', 'ur', or 'hinglish'.
    """
    text = message.lower().strip()
    
    # Check for Urdu script characters (Urdu Unicode block: 0600-06FF)
    has_urdu_script = any('\u0600' <= char <= '\u06FF' for char in message)
    if has_urdu_script:
        return "ur"
        
    # Explicit request overrides
    if "speak in urdu" in text or "urdu mein bolo" in text or "urdu bol" in text:
        return "ur"
    if "speak in english" in text or "english mein bolo" in text:
        return "en"
    if "speak in hinglish" in text or "hinglish mein bolo" in text:
        return "hinglish"
        
    # Common Hinglish / Roman Urdu keywords
    hinglish_keywords = {
        "bhai", "kya", "dalein", "mausam", "kaisa", "hai", "zang", "lagna", "ki", 
        "se", "ko", "par", "pe", "fasal", "khet", "pani", "khad", "sy", 
        "sath", "mein", "me", "ajj", "meri", "fasl", "karun", "kharab", "ho", "gaya",
        "kaise", "kab", "karna", "krna", "gandum", "kapas", "mandi", "rate", "btao"
    }
    
    words = text.split()
    matched_hinglish = sum(1 for w in words if w in hinglish_keywords)
    
    # If there are Hinglish words, classify as Hinglish
    if matched_hinglish > 0:
        return "hinglish"
        
    # Check for basic greetings
    if "assalam" in text or "salam" in text or "walaikum" in text:
        return "ur"
        
    # Default fallback to English
    return "en"


def get_response_language(message: str) -> str:
    """
    Helper to determine the target language of the response.
    """
    return detect_language(message)
