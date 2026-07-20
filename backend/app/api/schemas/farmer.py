from pydantic import BaseModel


class FarmerProfile(BaseModel):
    id: int
    name: str | None = None
    district: str | None = None
    village: str | None = None
    preferred_language: str = "ur"
    phone: str | None = None
    email: str | None = None
    land_size: str | None = None
    primary_crops: str | None = None
    soil_type: str | None = None
    irrigation: str | None = None
    farming_type: str | None = None
    avatar_url: str | None = None
    is_guest: bool = False
    current_memory: dict = {}
    is_complete: bool = False

    model_config = {"from_attributes": True}


class FarmerUpdate(BaseModel):
    name: str | None = None
    district: str | None = None
    village: str | None = None
    preferred_language: str | None = None
    phone: str | None = None
    email: str | None = None
    land_size: str | None = None
    primary_crops: str | None = None
    soil_type: str | None = None
    irrigation: str | None = None
    farming_type: str | None = None
