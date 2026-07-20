from sqlalchemy.orm import Session
from app.weather_service import get_weather_data
from app.rag.retriever import AgricultureRetriever
from app.models import User

# Keep a single global instance of retriever
retriever = AgricultureRetriever()


class CropAgent:
    def get_context(self, db: Session, query: str, user_memory: dict) -> str:
        """Retrieve crop science and cultivation data from PARC PDFs."""
        docs = retriever.search(db, query, user_memory, limit=2)
        ctx = "--- CROP ADVISORY (RAG SOURCE) ---\n"
        for doc in docs:
            ctx += f"Source: {doc.title}\nSnippet: {doc.snippet}\n"
        return ctx


class WeatherAgent:
    async def get_context(self, district: str) -> str:
        """Fetch real localized forecasts and spray alerts using OpenWeather."""
        try:
            w = await get_weather_data(district or "Multan")
            temp = w.get("temperature", 32)
            cond = w.get("condition", "Sunny")
            hum = w.get("humidity", 60)
            wind = w.get("wind_kmh", 12)
            advs = "\n".join([f"- {a['title']}: {a['text']}" for a in w.get("advisories", [])])
            
            return (
                "--- WEATHER CONTEXT ---\n"
                f"Location: {district or 'Multan'}\n"
                f"Temperature: {temp}°C, Condition: {cond}\n"
                f"Humidity: {hum}%, Wind: {wind} km/h\n"
                "Advisories:\n"
                f"{advs}\n"
            )
        except Exception as e:
            return f"--- WEATHER CONTEXT ---\nWeather data currently unavailable ({e}).\n"


class MarketAgent:
    def get_context(self, crop: str) -> str:
        """Simulate mandi market rates for Pakistani regions."""
        crop_clean = (crop or "cotton").lower().strip()
        rates = {
            "wheat": "Multan Mandi: Rs. 4,100/maund, Faisalabad Mandi: Rs. 4,050/maund.",
            "rice": "Gujranwala Mandi: Rs. 5,200/maund (Basmati), Larkana Mandi: Rs. 4,800/maund.",
            "cotton": "Multan Mandi: Rs. 8,600/maund, Hyderabad Mandi: Rs. 8,400/maund.",
            "mustard": "Khanewal Mandi: Rs. 7,100/maund, Sahiwal Mandi: Rs. 7,000/maund.",
            "tomatoes": "Lahore Mandi: Rs. 120/kg, Karachi Mandi: Rs. 140/kg."
        }
        matched = rates.get(crop_clean, "Multan Mandi: Rs. 5,500/maund, Faisalabad Mandi: Rs. 5,400/maund.")
        return (
            "--- MARKET PRICES (MANDI RATES) ---\n"
            f"Crop: {crop_clean.capitalize()}\n"
            f"Rates: {matched}\n"
        )


class PestAgent:
    def get_context(self, crop: str, district: str) -> str:
        """Retrieve active pest warnings for the region."""
        crop_clean = (crop or "cotton").lower().strip()
        if "cotton" in crop_clean:
            pest = "Whitefly and Thrips warnings active in southern Punjab. Keep monitoring underside of leaves."
        elif "wheat" in crop_clean:
            pest = "Yellow Rust (Peela Zang) warnings issued due to humidity. Spray fungicide before rain."
        else:
            pest = "No active major pest alerts for this crop in your district."
            
        return (
            "--- REGIONAL PEST WARNINGS ---\n"
            f"Alert: {pest}\n"
        )


class AgentOrchestrator:
    def __init__(self) -> None:
        self.crop_agent = CropAgent()
        self.weather_agent = WeatherAgent()
        self.market_agent = MarketAgent()
        self.pest_agent = PestAgent()

    async def gather_context(self, db: Session, user_id: str, query: str) -> tuple[str, list[str]]:
        """
        Coordinates all agents to build a synthesized context block.
        Returns (context_block, list_of_agents_used).
        """
        user = db.query(User).filter(User.user_id == user_id).first()
        district = user.location_district if user else "Multan"
        crop = user.soil_type or "cotton" # using soil_type or fallback
        # Let's extract crop name from query if mentioned
        for word in ["wheat", "rice", "cotton", "mustard", "tomato", "potato"]:
            if word in query.lower():
                crop = word
                break

        agents_used = []

        # 1. Crop science
        crop_ctx = self.crop_agent.get_context(db, query, {"current_crop": crop, "district": district})
        agents_used.append("CropAgent")

        # 2. Weather
        weather_ctx = await self.weather_agent.get_context(district)
        agents_used.append("WeatherAgent")

        # 3. Market
        market_ctx = self.market_agent.get_context(crop)
        agents_used.append("MarketAgent")

        # 4. Pest warning
        pest_ctx = self.pest_agent.get_context(crop, district)
        agents_used.append("PestAgent")

        # Synthesize into one context block
        synthesized = (
            f"{crop_ctx}\n"
            f"{weather_ctx}\n"
            f"{market_ctx}\n"
            f"{pest_ctx}\n"
        )
        return synthesized, agents_used
