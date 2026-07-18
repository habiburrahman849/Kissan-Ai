from fastapi import APIRouter, Query

from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])
service = WeatherService()


@router.get("/current")
async def current_weather(city: str = Query(default="Mardan,PK")):
    return await service.get_weather(city)
