from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.crop import CropHarvestRequest, CropStartRequest
from app.db.models import CropCycle, FarmEvent
from app.db.session import get_db
from app.memory.mem0_client import Mem0Client

router = APIRouter(prefix="/crops", tags=["crops"])
memory = Mem0Client()
post_msg = "Crop cycle started"


@router.post("/start")
def start_crop(payload: CropStartRequest, db: Session = Depends(get_db)):
    farmer = memory.ensure_farmer(db, payload.farmer_id)
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
    return {"message": post_msg, "crop_cycle_id": crop.id}


@router.post("/harvest")
def harvest_crop(payload: CropHarvestRequest, db: Session = Depends(get_db)):
    if payload.crop_cycle_id:
        crop = db.get(CropCycle, payload.crop_cycle_id)
        if crop:
            crop.status = "archived"
    else:
        memory.archive_active_crop(db, payload.farmer_id)
    db.add(FarmEvent(farmer_id=payload.farmer_id, event_type="harvest", description="Harvest completed"))
    db.commit()
    return {"message": "Crop memory archived for next season"}
