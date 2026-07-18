from __future__ import annotations

import httpx

from app.config import get_settings

KISSAN_AI_SYSTEM_PROMPT = """# KISSAN AI — System Prompt v1.0
## Hackathon: Qwen Cloud Global AI Hackathon | Track: MemoryAgent

---

### ROLE
You are **Kissan AI** — an intelligent agricultural assistant for Pakistani farmers. You have deep knowledge of Pakistani crops, weather patterns, soil types, pests, and market prices. You speak the farmer's language naturally.

---

### LANGUAGE RULES (STRICT — FOLLOW EXACTLY)

| User Input Language | Your Response Language | Detection Pattern |
|---------------------|----------------------|-----------------|
| **English** | Reply in **English** | Standard English words, grammar |
| **Urdu** (اردو script) | Reply in **Urdu** | Urdu/Persian script: گندم، فصل، پانی |
| **Hinglish / Roman Urdu** | Reply in **Hinglish / Roman Urdu** | English letters + Urdu words mixed: "meri fasl", "kya karun", "bhai help" |
| **English + "speak in Urdu"** | Reply in **Urdu** (اردو script) | Explicit request to switch |
| **Voice message** | Detect language from voice → reply in SAME language | Audio input detected |

**IMPORTANT:**
- If user says "Assalam o alaikum" → **Urdu** response
- If user says "Hi bro" → **Hinglish** response
- If user says "Hello, can you help me?" → **English** response
- If user says "bhai mera cotton kharab ho gaya" → **Hinglish** response
- If user says "speak in urdu / urdu mein bolo" → Switch to **Urdu** (اردو)

---

### IMAGE HANDLING
When user sends an image:
> "Main ne aapki tasveer dekh li hai. Crop disease detect karne ka feature jald aa raha hai. Abhi aap apni fasl ke baare mein bataein, main madad karunga."

(Translation: "I have seen your image. The crop disease detection feature is coming soon. For now, tell me about your crop and I will help.")

---

### MEMORY SYSTEM (CRITICAL FOR HACKATHON)
You have access to farmer memory. ALWAYS check memory before responding:

**Memory Layers:**
1. **Profile Memory**: Name, location (tehsil, district), land size, soil type
2. **Season Memory**: Current crop, variety, sowing date, fertilizer used
3. **Problem Memory**: Past diseases, pests, treatments tried, what worked
4. **Conversation Memory**: Last 10 chats with this farmer
5. **Knowledge Memory**: Best practices from training data

**Before every response:**
- Check: "Is this farmer returning? What do I know about them?"
- Reference past conversations naturally: "Aap ne pehle bhi poocha tha..."
- Use their location for localized advice: "Faisalabad mein abhi garmi zyada hai..."

---

### RAG KNOWLEDGE (YOUR PDFs)
You have been trained on these Pakistani agriculture documents:
- PARC crop cultivation guides
- Punjab/Sindh pest management manuals
- Fertilizer recommendations
- Irrigation schedules
- Market price reports

**When answering:**
- Cite the document source when possible: "PARC guide ke mutabiq..."
- Prioritize PDF knowledge over general knowledge for Pakistani crops
- If unsure, say: "Main aapke PDF data mein check kar ke batata hoon"

---

### RESPONSE STYLE

**Tone:** Friendly, respectful, like a knowledgeable village elder (wadero) or extension officer.

**Examples:**

| Situation | English | Hinglish | Urdu |
|-----------|---------|----------|------|
| Greeting | "Assalam o alaikum Ahmad bhai! How can I help your crops today?" | "Walaikum assalam Ahmad bhai! Aaj kya madad chahiye?" | "وعلیکم السلام احمد بھائی! آج کیا مدد چاہیے؟" |
| Wheat disease | "Your wheat shows yellow rust symptoms. Spray propiconazole before rain." | "Aapke gehu mein peela zang hai. Barish se pehle propiconazole spray karein." | "آپ کے گندم میں پیلا زنگ ہے۔ بارش سے پہلے پروپیکونازول سپرے کریں۔" |
| Market price | "Cotton rate in Multan mandi is Rs. 8,500/maund today." | "Multan mandi mein cotton ka rate 8,500 rupay man hai." | "ملتان منڈی میں کپاس کا ریٹ 8500 روپے من ہے۔" |

**Always:**
- Use local units: acres, kanal, maund, kg
- Mention local varieties: CP-77400, NIAB-878, Super Basmati
- Reference Pakistani seasons: Kharif, Rabi, Zaid
- Mention local mandis: Multan, Faisalabad, Larkana, Hyderabad

---

### PROACTIVE ALERTS (When Enabled)
If weather/market data available:
- "Ahmad bhai, kal Faisalabad mein barish ka imkan hai — aaj spray kar lo."
- "Cotton rate 500 rupay barh gaya hai — ab bechna behtar hai."

---

### TOOLS AVAILABLE
1. **weather_check** (location) → Current + forecast
2. **market_price** (crop, mandi) → Latest rates
3. **pest_alert** (crop, location) → Current pest warnings
4. **disease_diagnose** (symptoms) → From PDF knowledge
5. **memory_recall** (farmer_id) → Past interactions
6. **memory_store** (farmer_id, data) → Save new info

---

### SAFETY
- Never recommend banned pesticides in Pakistan
- Always suggest: "Pehle apne area ke extension officer se mashwara karein"
- For serious crop failures: suggest contacting PARC or local agriculture office

---

### OUTPUT FORMAT
Respond in clean text. Use emojis sparingly (🌾 for crops, 🌧️ for weather, 💰 for prices). Keep responses under 150 words for mobile users."""


def detect_language(message: str) -> str:
    text = message.lower()
    
    # 1. Image checks: if the message refers to an image or photo
    image_keywords = ["image", "photo", "pic", "upload", "تصویر", "فوٹو", "tasveer", "taswir"]
    if any(kw in text for kw in image_keywords):
        return "Image"
        
    # 2. Check uRdU: User explicitly says "English" but asks to chat in Urdu
    if "speak in urdu" in text or "urdu mein bolo" in text:
        return "uRdU"
    if "urdu" in text and ("chat" in text or "speak" in text or "tell" in text or "write" in text or "in" in text):
        return "uRdU"
        
    # 3. Explicit check for greeting or switches
    if "assalam o alaikum" in text or "assalamu alaikum" in text or "assalam-o-alaikum" in text:
        return "URDU"
        
    # 4. Check Urdu script characters (Urdu Unicode block: 0600-06FF)
    has_urdu = any('\u0600' <= char <= '\u06FF' for char in message)
    if has_urdu:
        return "URDU"
        
    # 5. Check if user explicitly says "hi bro"
    if "hi bro" in text:
        return "Hinshlish"
        
    # 6. Check Hinshlish / Roman Urdu keywords
    hinglish_keywords = [
        "bhai", "kya", "dalein", "mausam", "kaisa", "hai", "zang", "lagna", "ki", 
        "se", "ko", "par", "pe", "fasal", "khet", "pani", "khad", "sy", 
        "sath", "mein", "me", "ajj", "meri", "fasl", "karun", "kharab", "ho", "gaya"
    ]
    words = text.split()
    is_hinglish = any(word in hinglish_keywords for word in words)
    if is_hinglish:
        return "Hinshlish"
        
    # Default is English
    return "English"


def is_profile_incomplete(memory: dict) -> bool:
    defaults = {
        "farmer_name": "Ahmad",
        "phone": "+92 300 1234567",
        "email": "ahmad@kissan.ai",
        "district": "Mardan",
        "village": "Rustam",
    }
    
    fields_to_check = [
        "farmer_name", "phone", "email", "district", "village",
        "land_size", "primary_crops", "soil_type", "irrigation", "farming_type"
    ]
    for field in fields_to_check:
        val = memory.get(field)
        if not val:
            return True
        if field in defaults and val == defaults[field]:
            return True
            
    return False


class QwenClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_urdu_answer(self, farmer_message: str, memory: dict, science: list[dict], history: list[dict] | None = None) -> tuple[str, str]:
        if self.settings.qwen_api_base and self.settings.qwen_api_key:
            try:
                return await self._call_remote_qwen(farmer_message, memory, science, history), "qwen"
            except Exception:
                return self._development_answer(farmer_message, memory, science), "mock"
        return self._development_answer(farmer_message, memory, science), "mock"

    async def _call_remote_qwen(self, farmer_message: str, memory: dict, science: list[dict], history: list[dict] | None = None) -> str:
        messages = [
            {
                "role": "system",
                "content": KISSAN_AI_SYSTEM_PROMPT,
            }
        ]
        if history:
            for msg in history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })
        
        messages.append({
            "role": "user",
            "content": (
                f"Farmer message: {farmer_message}\n"
                f"Farmer memory: {memory}\n"
                f"Scientific context: {science}"
            ),
        })

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.settings.qwen_api_base.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.qwen_api_key}"},
                json={
                    "model": self.settings.qwen_model,
                    "messages": messages,
                    "temperature": 0.35,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _development_answer(self, farmer_message: str, memory: dict, science: list[dict]) -> str:
        lang = detect_language(farmer_message)
        crop = memory.get("current_crop")
        village = memory.get("village") or "آپ کے علاقے"
        
        # Determine base answer
        if lang == "Image":
            answer = "Main ne aapki tasveer dekh li hai. Crop disease detect karne ka feature jald aa raha hai. Abhi aap apni fasl ke baare mein bataein, main madad karunga."
        elif lang in ("URDU", "uRdU"):
            if "assalam" in farmer_message.lower():
                answer = "وعلیکم السلام احمد بھائی! آج کیا مدد چاہیے؟"
            elif crop == "mustard" and ("پیلے" in farmer_message or "yellow" in farmer_message.lower()):
                answer = (
                    f"{village} میں آپ کی سرسوں کی فصل کے پتوں پر پیلے دھبے آلٹرنیریا بلائٹ کی علامت ہو سکتے ہیں۔ "
                    "پہلے متاثرہ پتوں کو دیکھیں کہ دھبوں کے کنارے بھورے یا سیاہ تو نہیں۔ پانی پتوں پر کھڑا نہ رہنے دیں، "
                    "کھیت میں ہوا کا گزر بہتر رکھیں، اور قریبی زرعی ماہر سے مقامی رجسٹرڈ فنجی سائیڈ کی مقدار کی تصدیق کر کے سپرے کریں۔"
                )
            elif crop:
                answer = (
                    f"آپ کی موجودہ فصل {crop} کے حساب سے مسئلہ نوٹ کر لیا گیا ہے۔ "
                    "براہ کرم پتے کی صاف تصویر، فصل کی عمر، آخری کھاد، اور آبپاشی کی تاریخ بھی بتا دیں تاکہ زیادہ درست مشورہ دیا جا سکے۔"
                )
            else:
                answer = (
                    "براہ کرم اپنی فصل کا نام، گاؤں/ضلع، فصل کی عمر، اور مسئلے کی تصویر یا علامات بتائیں۔ "
                    "اس کے بعد میں آپ کو اردو میں واضح اور مقامی مشورہ دوں گا۔"
                )
        elif lang == "Hinshlish":
            if "hi bro" in farmer_message.lower():
                answer = "Walaikum assalam Ahmad bhai! Aaj kya madad chahiye?"
            elif crop == "mustard" and ("پیلے" in farmer_message or "yellow" in farmer_message.lower()):
                answer = (
                    f"{village} mein aap ki mustard crop ke leaves par yellow spots Alternaria blight ho sakta hai. "
                    "Pani leaves par khara na hone dein, field mein airflow behtar rakhein, aur local agricultural expert se fungicide spray ki confirmation lein."
                )
            elif crop:
                answer = (
                    f"Aap ki crop {crop} ke mutabiq problem note kar li hai. "
                    "Please leaves ki photo, crop age, last fertilizer aur irrigation details share karein taakay behtar mashwara diya ja sakay."
                )
            else:
                answer = (
                    "Please apni crop ka naam, village/district, crop age, aur problems batayein. "
                    "Iske baad mein aap ko Roman Urdu mein behtar guidance doonga."
                )
        else: # English
            if "hello" in farmer_message.lower() or "help" in farmer_message.lower():
                answer = "Assalam o alaikum Ahmad bhai! How can I help your crops today?"
            elif crop == "mustard" and ("yellow" in farmer_message.lower()):
                answer = (
                    f"Yellow spots on your mustard crop in {village} could be a sign of Alternaria blight. "
                    "Avoid standing water on leaves, maintain proper airflow in the field, and consult a local expert for recommended fungicide application."
                )
            elif crop:
                answer = (
                    f"Your concern regarding the {crop} crop has been noted. "
                    "Please share clear photos of leaves, crop age, last fertilizer used, and irrigation details for customized advice."
                )
            else:
                answer = (
                    "Please provide your crop name, age, village/district, and specific symptoms or problems "
                    "so I can provide accurate farming guidance."
                )
                
        # Append profile completion alert if profile is incomplete (except for Image replies to keep them focused)
        if lang != "Image" and is_profile_incomplete(memory):
            if lang in ("URDU", "uRdU"):
                answer += "\n\n⚠️ نوٹ: آپ کا پروفائل مکمل نہیں ہے۔ براہ کرم ذاتی اور درست مشورہ حاصل کرنے کے لیے 'Profile' پیج پر جا کر اپنی معلومات مکمل کریں۔"
            elif lang == "Hinshlish":
                answer += "\n\n⚠️ Note: Aap ka profile incomplete hai. Sahi aur personalized mashwaray ke liye please 'Profile' page par ja kar apni details complete karein."
            else:
                answer += "\n\n⚠️ Note: Your profile is incomplete. Please go to the 'Profile' page and complete your information to receive personalized agricultural advice."
                
        return answer
