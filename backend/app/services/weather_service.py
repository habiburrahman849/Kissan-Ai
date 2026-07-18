from __future__ import annotations

from collections import defaultdict
from datetime import datetime

import httpx

from app.config import get_settings


class WeatherService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def get_weather(self, city: str = "Mardan,PK") -> dict:
        if not self.settings.openweather_api_key:
            return self._fallback(city)

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                current_response = await client.get(
                    "https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "q": city,
                        "appid": self.settings.openweather_api_key,
                        "units": "metric",
                    },
                )
                current_response.raise_for_status()
                current = current_response.json()

                forecast_response = await client.get(
                    "https://api.openweathermap.org/data/2.5/forecast",
                    params={
                        "q": city,
                        "appid": self.settings.openweather_api_key,
                        "units": "metric",
                    },
                )
                forecast_response.raise_for_status()
                forecast = forecast_response.json()
                return self._shape(current, forecast)
        except Exception:
            return self._fallback(city)

    def _shape(self, current: dict, forecast: dict) -> dict:
        weather = current.get("weather", [{}])[0]
        rain = current.get("rain", {}).get("1h") or current.get("rain", {}).get("3h") or 0
        shaped_forecast = self._daily_forecast(forecast.get("list", []))
        payload = {
            "location": f"{current.get('name', 'Mardan')}, {current.get('sys', {}).get('country', 'PK')}",
            "temperature": round(current.get("main", {}).get("temp", 0)),
            "condition": weather.get("description", "clear sky").title(),
            "icon": weather.get("icon", "01d"),
            "humidity": current.get("main", {}).get("humidity", 0),
            "wind_kmh": round(current.get("wind", {}).get("speed", 0) * 3.6),
            "rain_mm": rain,
            "pressure": current.get("main", {}).get("pressure", 0),
            "forecast": shaped_forecast,
        }
        payload["advisories"] = self._advisories(payload)
        return payload

    def _daily_forecast(self, items: list[dict]) -> list[dict]:
        grouped: dict[str, list[dict]] = defaultdict(list)
        for item in items:
            date_key = item.get("dt_txt", "").split(" ")[0]
            if date_key:
                grouped[date_key].append(item)

        days = []
        for date_key, day_items in list(grouped.items())[:5]:
            temps = [entry.get("main", {}).get("temp", 0) for entry in day_items]
            rain_chance = max([entry.get("pop", 0) for entry in day_items] or [0])
            weather = day_items[len(day_items) // 2].get("weather", [{}])[0]
            date_obj = datetime.fromisoformat(date_key)
            days.append(
                {
                    "day": date_obj.strftime("%a"),
                    "temp": round(sum(temps) / len(temps)),
                    "min": round(min(temps)),
                    "max": round(max(temps)),
                    "rain_percent": round(rain_chance * 100),
                    "icon": weather.get("icon", "01d"),
                    "condition": weather.get("main", "Clear"),
                }
            )
        return days

    def _advisories(self, payload: dict) -> list[dict]:
        advisories = []
        if payload["rain_mm"] or any(day["rain_percent"] >= 60 for day in payload["forecast"][:2]):
            advisories.append(
                {
                    "type": "water",
                    "title": "Irrigation: Hold watering",
                    "text": "Rain is likely soon. Delay irrigation and avoid spraying until leaves are dry.",
                    "tone": "blue",
                }
            )
        if payload["wind_kmh"] >= 15:
            advisories.append(
                {
                    "type": "spray",
                    "title": "Spray Alert: Wind is high",
                    "text": "Postpone pesticide or fungicide spray until wind drops for better coverage.",
                    "tone": "orange",
                }
            )
        if payload["humidity"] >= 70:
            advisories.append(
                {
                    "type": "disease",
                    "title": "Disease Watch: High humidity",
                    "text": "Scout leaves for fungal spots and keep airflow clear around the crop.",
                    "tone": "green",
                }
            )
        if not advisories:
            advisories.append(
                {
                    "type": "field",
                    "title": "Field Work: Good window",
                    "text": "Conditions look workable. Continue normal scouting and irrigation checks.",
                    "tone": "green",
                }
            )
        return advisories

    def _fallback(self, city: str) -> dict:
        payload = {
            "location": city,
            "temperature": 32,
            "condition": "Clear",
            "icon": "01d",
            "humidity": 55,
            "wind_kmh": 9,
            "rain_mm": 0,
            "pressure": 1010,
            "forecast": [
                {"day": "Today", "temp": 32, "min": 27, "max": 35, "rain_percent": 10, "icon": "01d", "condition": "Clear"}
            ],
        }
        payload["advisories"] = self._advisories(payload)
        return payload
