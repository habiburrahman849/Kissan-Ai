from __future__ import annotations

import json
import re
import httpx

from app.config import get_settings

URDU_CROP_ALIASES = {
    "گندم": "wheat",
    "سرسوں": "mustard",
    "کپاس": "cotton",
    "چاول": "rice",
    "دھان": "rice",
    "مکئی": "maize",
}

ENGLISH_CROPS = {"wheat", "mustard", "cotton", "rice", "maize", "tomato", "potato"}


def extract_memory_facts_fallback(message: str) -> dict:
    text = message.lower()
    facts: dict = {}

    for crop in ENGLISH_CROPS:
        if crop in text:
            facts["current_crop"] = crop

    for urdu, english in URDU_CROP_ALIASES.items():
        if urdu in message:
            facts["current_crop"] = english

    if "urea" in text or "یوریا" in message:
        facts["last_fertilizer"] = "urea"

    if any(word in text for word in ["harvest", "harvested"]) or any(word in message for word in ["کٹائی", "فصل کاٹ"]):
        facts["season_status"] = "harvested"

    symptom_patterns = [
        ("yellow_spots", ["yellow spot", "yellow spots", "پیلے دھبے", "زرد دھبے"]),
        ("wilting", ["wilt", "wilting", "مرجھا", "سوکھ"]),
        ("pest", ["pest", "insect", "کیڑا", "سنڈی"]),
    ]
    symptoms = [name for name, terms in symptom_patterns if any(term in text or term in message for term in terms)]
    if symptoms:
        facts["recent_symptoms"] = symptoms

    days_match = re.search(r"(\d+)\s*(day|days|دن)", text)
    if days_match and facts.get("last_fertilizer"):
        facts["last_fertilizer_days_ago"] = int(days_match.group(1))

    return facts


async def extract_memory_facts(message: str) -> dict:
    settings = get_settings()
    if not settings.qwen_api_key or not settings.qwen_api_base:
        return extract_memory_facts_fallback(message)

    prompt = (
        "You are an expert information extraction assistant for agriculture.\n"
        "Analyze the farmer's input message (in English, Urdu, or Roman Urdu) and extract any information about the farmer's identity, location, farm characteristics, crop cycles, and recent farm events.\n"
        "Extract the following fields in JSON format:\n"
        "- name: farmer's name (string)\n"
        "- district: farming district in Pakistan (string)\n"
        "- village: village name (string)\n"
        "- land_size: size of land, e.g., '5 acres', '10 kanals' (string)\n"
        "- primary_crops: crops they mention growing generally (string)\n"
        "- soil_type: e.g., sandy, clay, loam (string)\n"
        "- irrigation: e.g., canal, tube well, drip, rainfed (string)\n"
        "- farming_type: e.g., organic, conventional (string)\n"
        "- current_crop: current crop name, normalized to standard English name: wheat, cotton, rice, maize, mustard, tomato, potato, sugarcane, etc. (string)\n"
        "- variety: specific seed variety, e.g., FH-142, NIAB-878, Super Basmati (string)\n"
        "- sowing_date: when it was sowed, e.g., 'last week', '10 days ago' (string)\n"
        "- last_fertilizer: type of fertilizer, e.g., urea, dap, npk (string)\n"
        "- last_fertilizer_days_ago: number of days ago fertilizer was applied (integer)\n"
        "- recent_symptoms: list of symptoms, e.g., ['yellow_spots', 'wilting', 'pest'] (array of strings)\n"
        "- season_status: 'sowing', 'active', 'harvested' (string)\n\n"
        "Return ONLY a valid JSON object. Do not include any explanation or markdown formatting outside of JSON. "
        "If any field is not mentioned or cannot be inferred, set its value to null.\n\n"
        f"Farmer Message: {message}"
    )

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{settings.qwen_api_base.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {settings.qwen_api_key}"},
                json={
                    "model": settings.qwen_model,
                    "messages": [
                        {"role": "system", "content": "You are a precise data extraction agent. Output JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"}
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            # Clean possible markdown block formatting
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\n", "", content)
                content = re.sub(r"\n```$", "", content)
            
            extracted = json.loads(content.strip())
            # Clean null or empty fields so they don't overwrite existing memory with nulls
            filtered = {k: v for k, v in extracted.items() if v is not None}
            return filtered
    except Exception as e:
        print(f"Memory extraction via Qwen failed: {e}. Falling back to regex.")
        return extract_memory_facts_fallback(message)

