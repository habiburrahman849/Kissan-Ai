from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.farmer import FarmerProfile, FarmerUpdate
from app.db.models import Farmer
from app.db.session import get_db
from app.memory.mem0_client import Mem0Client

router = APIRouter(prefix="/farmers", tags=["farmers"])
memory = Mem0Client()


@router.get("/me", response_model=FarmerProfile)
def get_me(farmer_id: int = 1, db: Session = Depends(get_db)):
    farmer = memory.ensure_farmer(db, farmer_id)
    profile = FarmerProfile.model_validate(farmer)
    profile.current_memory = memory.get_profile(db, farmer.id)
    
    from app.llm.qwen_client import is_profile_incomplete
    profile.is_complete = not is_profile_incomplete(profile.current_memory)
    return profile


@router.put("/me", response_model=FarmerProfile)
def update_me(payload: FarmerUpdate, farmer_id: int = 1, db: Session = Depends(get_db)):
    farmer = memory.ensure_farmer(db, farmer_id)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(farmer, field, value)
    db.commit()
    db.refresh(farmer)
    profile = FarmerProfile.model_validate(farmer)
    profile.current_memory = memory.get_profile(db, farmer.id)
    
    from app.llm.qwen_client import is_profile_incomplete
    profile.is_complete = not is_profile_incomplete(profile.current_memory)
    return profile
