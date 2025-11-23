from fastapi import HTTPException, Header, Depends
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import users_collection
import argon2

# Security config
SECRET_KEY = "1234"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 1 day

# Argon2 password hasher
ph = argon2.PasswordHasher()

fake_db = {}

def hash_password(password: str) -> str:
    """Hash password using Argon2"""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against Argon2 hash"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False
    except Exception:
        return False

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(authorization: str = Header(...)) -> str:
    """Extract user email from JWT token"""
    try:
        token = authorization.split(" ")[1]  # Strip "Bearer "
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # user email
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
