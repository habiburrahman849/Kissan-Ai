from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.farmer import FarmerProfile, FarmerUpdate
from app.core.auth import get_current_farmer
from app.db.models import Farmer
from app.db.session import get_db
from app.llm.qwen_client import is_profile_incomplete
from app.memory.mem0_client import Mem0Client

router = APIRouter(prefix="/farmers", tags=["farmers"])
memory = Mem0Client()


@router.get("/me", response_model=FarmerProfile)
def get_me(farmer: Farmer = Depends(get_current_farmer), db: Session = Depends(get_db)):
    profile = FarmerProfile.model_validate(farmer)
    profile.current_memory = memory.get_profile(db, farmer.id)
    profile.is_complete = not is_profile_incomplete(profile.current_memory)
    profile.avatar_url = farmer.avatar_url
    profile.is_guest = bool(farmer.is_guest)
    return profile


@router.put("/me", response_model=FarmerProfile)
def update_me(
    payload: FarmerUpdate,
    farmer: Farmer = Depends(get_current_farmer),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(farmer, field, value)
    db.commit()
    db.refresh(farmer)
    profile = FarmerProfile.model_validate(farmer)
    profile.current_memory = memory.get_profile(db, farmer.id)
    profile.is_complete = not is_profile_incomplete(profile.current_memory)
    profile.avatar_url = farmer.avatar_url
    profile.is_guest = bool(farmer.is_guest)
    return profile
