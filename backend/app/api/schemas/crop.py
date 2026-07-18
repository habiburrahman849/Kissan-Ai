from pydantic import BaseModel


class CropStartRequest(BaseModel):
    farmer_id: int = 1
    crop_name: str
    variety: str | None = None
    sowing_date: str | None = None


class CropHarvestRequest(BaseModel):
    farmer_id: int = 1
    crop_cycle_id: int | None = None
