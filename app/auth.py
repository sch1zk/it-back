from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
import os
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from app import crud, database
from app.schemas import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class DeveloperOAuth2PasswordBearer(OAuth2PasswordBearer):
    pass

class EmployerOAuth2PasswordBearer(OAuth2PasswordBearer):
    pass

oauth2_scheme_developer = DeveloperOAuth2PasswordBearer(tokenUrl="developer/token")
oauth2_scheme_employer = EmployerOAuth2PasswordBearer(tokenUrl="employer/token")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

ALGORITHM = os.getenv("ALGORITHM")
if not ALGORITHM:
    raise ValueError("ALGORITHM environment variable is not set")

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES environment variable is not set")
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_developer(db: Session, username: str, password: str):
    user = crud.get_developer(db, "username", username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def authenticate_employer(db: Session, username: str, password: str):
    user = crud.get_employer(db, "username", username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_developer(token: Annotated[str, Depends(oauth2_scheme_developer)], db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = crud.get_developer(db, "username", username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_employer(token: Annotated[str, Depends(oauth2_scheme_employer)], db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = crud.get_employer(db, "username", username)
    if user is None:
        raise credentials_exception
    return user
