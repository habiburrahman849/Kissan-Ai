from __future__ import annotations

import re


URDU_CROP_ALIASES = {
    "گندم": "wheat",
    "سرسوں": "mustard",
    "کپاس": "cotton",
    "چاول": "rice",
    "دھان": "rice",
    "مکئی": "maize",
}

ENGLISH_CROPS = {"wheat", "mustard", "cotton", "rice", "maize", "tomato", "potato"}


def extract_memory_facts(message: str) -> dict:
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
