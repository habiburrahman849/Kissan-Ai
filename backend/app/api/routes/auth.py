import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User, Conversation, FarmEvent, Memory
from app.core.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class GuestResponse(BaseModel):
    user_id: str
    access_token: str
    message: str


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    full_name: str | None = None
    guest_user_id: str | None = None


class RegisterResponse(BaseModel):
    user_id: str
    access_token: str
    message: str


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3)
    password: str


class LoginResponse(BaseModel):
    user_id: str
    access_token: str
    message: str


class MeResponse(BaseModel):
    user_id: str
    email: str | None
    full_name: str | None
    is_guest: bool


def _transfer_guest_data(db: Session, guest_user_id: str, target_user_id: str):
    if not guest_user_id or guest_user_id == target_user_id:
        return
    try:
        db.query(Conversation).filter(Conversation.user_id == guest_user_id).update(
            {Conversation.user_id: target_user_id}, synchronize_session=False
        )
        db.query(FarmEvent).filter(FarmEvent.user_id == guest_user_id).update(
            {FarmEvent.user_id: target_user_id}, synchronize_session=False
        )
        db.query(Memory).filter(Memory.user_id == guest_user_id).update(
            {Memory.user_id: target_user_id}, synchronize_session=False
        )
        guest_user = db.query(User).filter(User.user_id == guest_user_id).first()
        target_user = db.query(User).filter(User.user_id == target_user_id).first()
        if guest_user and target_user:
            if guest_user.location_district and not target_user.location_district:
                target_user.location_district = guest_user.location_district
            if guest_user.location_tehsil and not target_user.location_tehsil:
                target_user.location_tehsil = guest_user.location_tehsil
            if guest_user.land_size_acres and not target_user.land_size_acres:
                target_user.land_size_acres = guest_user.land_size_acres
            if guest_user.soil_type and not target_user.soil_type:
                target_user.soil_type = guest_user.soil_type
            db.delete(guest_user)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error transferring guest data: {e}")


@router.post("/guest", response_model=GuestResponse)
def guest_login(db: Session = Depends(get_db)):
    guest_id = f"guest_{uuid.uuid4().hex[:8]}"
    
    # Save guest user
    user = User(
        user_id=guest_id,
        full_name="Guest Farmer",
        is_guest=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(guest_id)
    return GuestResponse(
        user_id=guest_id,
        access_token=token,
        message="Guest session started successfully"
    )


@router.post("/register", response_model=RegisterResponse)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    if "@" not in email_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered, please login"
        )

    # Create new registered user
    new_user_id = f"user_{uuid.uuid4().hex[:8]}"
    hashed = hash_password(payload.password)
    
    user = User(
        user_id=new_user_id,
        email=email_clean,
        password_hash=hashed,
        full_name=payload.full_name or "Farmer",
        is_guest=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Transfer guest data if applicable
    if payload.guest_user_id:
        _transfer_guest_data(db, payload.guest_user_id, new_user_id)

    token = create_access_token(new_user_id)
    return RegisterResponse(
        user_id=new_user_id,
        access_token=token,
        message="User registered successfully"
    )


@router.post("/login", response_model=LoginResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    email_clean = payload.email.strip().lower()
    if "@" not in email_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    user = db.query(User).filter(User.email == email_clean).first()
    
    if not user or user.is_guest or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(user.user_id)
    return LoginResponse(
        user_id=user.user_id,
        access_token=token,
        message="Logged in successfully"
    )


@router.get("/me", response_model=MeResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return MeResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_guest=current_user.is_guest
    )
