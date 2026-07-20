import httpx
from app.config import get_settings

KISSAN_AI_SYSTEM_PROMPT = """# KISSAN AI — System Prompt v1.0
## Hackathon: Qwen Cloud Global AI Hackathon | Track: MemoryAgent

### ROLE
You are **Kissan AI** — an intelligent agricultural assistant for Pakistani farmers. You have deep knowledge of Pakistani crops, weather patterns, soil types, pests, and market prices. You speak the farmer's language naturally.

### LANGUAGE RULES (STRICT — FOLLOW EXACTLY)
- If user writes in **English** -> Reply in **English**
- If user writes in **Urdu** (اردو script) -> Reply in **Urdu**
- If user writes in **Hinglish / Roman Urdu** -> Reply in **Hinglish / Roman Urdu**
- If user explicitly says "speak in urdu" -> switch to Urdu.

### RESPONSE STYLE
- Tone: Friendly, respectful, like a knowledgeable extension officer.
- Use local units: acres, kanal, maund, kg.
- Keep responses under 150 words for mobile users.
"""


class QwenClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_response(
        self,
        message: str,
        system_context: str,
        history: list[dict] | None = None
    ) -> tuple[str, str]:
        """
        Sends the request to Qwen Cloud API.
        Returns (response_text, brain_mode).
        """
        api_key = (self.settings.qwen_api_key or "").strip()
        api_base = (self.settings.qwen_api_base or "https://dashscope-intl.aliyuncs.com/compatible-mode/v1").strip()
        model = (self.settings.qwen_model or "qwen-plus").strip()

        if not api_key:
            return self._fallback_answer(message, system_context), "mock"

        messages = [
            {"role": "system", "content": KISSAN_AI_SYSTEM_PROMPT + "\n\n" + system_context}
        ]

        if history:
            for item in history:
                messages.append({
                    "role": item.get("role", "user"),
                    "content": item.get("content", "")
                })

        messages.append({"role": "user", "content": message})

        try:
            async with httpx.AsyncClient(timeout=45) as client:
                res = await client.post(
                    f"{api_base.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.3,
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    answer = data["choices"][0]["message"]["content"]
                    return answer, "qwen"
                else:
                    print(f"Qwen API error status {res.status_code}: {res.text}")
                    return self._fallback_answer(message, system_context), "mock"
        except Exception as e:
            print(f"Qwen API connection error: {e}")
            return self._fallback_answer(message, system_context), "mock"

    def _fallback_answer(self, message: str, context: str) -> str:
        """Fallback offline answer synthesizer for development and fail-safe safety."""
        from app.language_detector import detect_language
        lang = detect_language(message)
        
        # Analyze context to extract crop / name
        crop = "crops"
        if "crop" in context.lower():
            for word in ["wheat", "rice", "cotton", "mustard", "tomatoes"]:
                if word in context.lower():
                    crop = word
                    break

        if lang == "ur":
            return (
                f"پیارے کسان بھائی، سرور پر بوجھ کی وجہ سے مقامی معلومات استعمال کی جا رہی ہیں۔ "
                f"آپ کی فصل {crop} کے لیے مشورہ ہے کہ کھاد کا متوازن استعمال کریں اور آبپاشی وقت پر کریں۔ "
                f"مزید رہنمائی کے لیے پتے کی تصویر شیئر کریں۔"
            )
        elif lang == "hinglish":
            return (
                f"Ahmad bhai, server busy hone ki wajah se local offline information use ho rahi hai. "
                f"Aapki {crop} crop ke liye mashwara hai ke fertilizer waqt par dalein aur barish se pehle spray se parhez karein. "
                f"Sahi guidance ke liye leaves ki clear photo share karein."
            )
        else:
            return (
                f"Dear farmer, offline safety fallback is active. "
                f"Regarding your {crop} crop: ensure timely weeding, balanced nitrogen application, and monitor weather warnings before spraying."
            )
