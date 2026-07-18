import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.llm.qwen_client import detect_language, QwenClient

def test_language_detection():
    # Test English
    assert detect_language("Hello, can you help me?") == "English"
    assert detect_language("What fertilizer should I use?") == "English"

    # Test Urdu
    assert detect_language("گندم کی فصل کے بارے میں بتائیں") == "URDU"
    assert detect_language("Assalam o alaikum") == "URDU"
    assert detect_language("assalamu alaikum") == "URDU"
    assert detect_language("speak in urdu") == "uRdU"
    assert detect_language("urdu mein bolo") == "uRdU"

    # Test Hinglish / Roman Urdu
    assert detect_language("Hi bro") == "Hinshlish"
    assert detect_language("bhai mera cotton kharab ho gaya") == "Hinshlish"
    assert detect_language("kya karun") == "Hinshlish"

    # Test Image
    assert detect_language("i uploaded a photo") == "Image"
    assert detect_language("tasveer") == "Image"
    
    print("All language detection tests passed!")


async def test_mock_answers():
    client = QwenClient()
    
    # 1. Test image response
    memory = {"current_crop": "mustard", "village": "Rustam"}
    ans, mode = await client.generate_urdu_answer("i uploaded a photo", memory, [])
    assert "Main ne aapki tasveer dekh li hai" in ans
    
    # 2. Test Urdu greeting response
    ans, mode = await client.generate_urdu_answer("Assalam o alaikum", memory, [])
    assert "وعلیکم السلام" in ans
    
    # 3. Test Hinglish greeting response
    ans, mode = await client.generate_urdu_answer("Hi bro", memory, [])
    assert "Walaikum assalam" in ans
    
    # 4. Test English greeting response
    ans, mode = await client.generate_urdu_answer("Hello, can you help me?", memory, [])
    assert "Assalam o alaikum Ahmad bhai! How can I help" in ans
    
    print("All mock answer tests passed!")


if __name__ == "__main__":
    test_language_detection()
    asyncio.run(test_mock_answers())
