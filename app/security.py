from pwdlib import PasswordHash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import jwt

password_hash = PasswordHash.recommended()
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password:str) -> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expires}
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set")
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)