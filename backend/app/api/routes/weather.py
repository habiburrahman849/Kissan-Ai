from fastapi import APIRouter, HTTPException
from app.weather_service import get_weather_data

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("")
async def get_weather(location: str | None = "Multan"):
    try:
        data = await get_weather_data(location)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
