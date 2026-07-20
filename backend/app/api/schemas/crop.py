from pydantic import BaseModel


class CropStartRequest(BaseModel):
    crop_name: str
    variety: str | None = None
    sowing_date: str | None = None


class CropHarvestRequest(BaseModel):
    crop_cycle_id: int | None = None
