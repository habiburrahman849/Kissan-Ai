from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.crop import CropHarvestRequest, CropStartRequest
from app.core.auth import get_current_farmer
from app.db.models import CropCycle, FarmEvent, Farmer
from app.db.session import get_db
from app.memory.mem0_client import Mem0Client

router = APIRouter(prefix="/crops", tags=["crops"])
memory = Mem0Client()


@router.post("/start")
def start_crop(
    payload: CropStartRequest,
    farmer: Farmer = Depends(get_current_farmer),
    db: Session = Depends(get_db),
):
    memory.archive_active_crop(db, farmer.id)
    crop = CropCycle(
        farmer_id=farmer.id,
        crop_name=payload.crop_name.lower(),
        variety=payload.variety,
        sowing_date=payload.sowing_date,
    )
    db.add(crop)
    db.add(FarmEvent(farmer_id=farmer.id, event_type="sowing", description=f"Started {payload.crop_name}"))
    db.commit()
    db.refresh(crop)
    return {"message": "Crop cycle started", "crop_cycle_id": crop.id}


@router.post("/harvest")
def harvest_crop(
    payload: CropHarvestRequest,
    farmer: Farmer = Depends(get_current_farmer),
    db: Session = Depends(get_db),
):
    if payload.crop_cycle_id:
        crop = db.get(CropCycle, payload.crop_cycle_id)
        if crop and crop.farmer_id == farmer.id:
            crop.status = "archived"
    else:
        memory.archive_active_crop(db, farmer.id)
    db.add(FarmEvent(farmer_id=farmer.id, event_type="harvest", description="Harvest completed"))
    db.commit()
    return {"message": "Crop memory archived for next season"}
