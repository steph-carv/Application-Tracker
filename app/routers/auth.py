from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.database import get_session
from app.models import UserCreate, UserRead, User, Token
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserRead, status_code=201)
def signup_user(data: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == data.email.lower())).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    hashed_password = hash_password(data.password)
    user = User(email=data.email, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == form.username.lower())).first()
    if not existing_user or not verify_password(form.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_access_token(existing_user.id), "token_type": "bearer"}
   