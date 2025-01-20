from datetime import datetime, timedelta, timezone
from typing import Annotated

# PyJWT
import jwt
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

import os

from app import crud, database
from app.schemas import TokenData

# Create an object for password hashing using the bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define two classes for handling OAuth2 authorization for different types of users
# The classes allow us to set different token URLs for getting tokens for developers and employers
class DeveloperOAuth2PasswordBearer(OAuth2PasswordBearer):
    pass # Currently no additional logic, class just inherits from OAuth2PasswordBearer

class EmployerOAuth2PasswordBearer(OAuth2PasswordBearer):
    pass # Same as above, but for employers (customers)

# Create authorization schemes for developers and employers
# Each type of user will have its own endpoint for obtaining tokens
oauth2_scheme_developer = DeveloperOAuth2PasswordBearer(tokenUrl="developer/token")
oauth2_scheme_employer = EmployerOAuth2PasswordBearer(tokenUrl="employer/token")

# Load authentication-related data from environment variables (.env)
# These are the secret key, algorithm, and token expiration time
SECRET_KEY = os.getenv("SECRET_KEY") # Secret key for signing JWT tokens
ALGORITHM = os.getenv("ALGORITHM") # Algorithm used to sign tokens (e.g., HS256)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")) # Token expiration time in minutes (from .env)

# Function to create an access token (JWT) for authentication
def create_access_token(data: dict, expires_delta: timedelta = None):
    # Create a copy of the data to avoid modifying the original input
    to_encode = data.copy()
    
    # Set the expiration time for the token. If `expires_delta` is provided, use it. 
    # Otherwise, use a default expiration time based on the environment variable.
    if expires_delta:
        # If a custom expiration time is provided, use it.
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # If no custom expiration is provided, use the default expiration time.
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add the expiration time ('exp') to the data to be encoded in the JWT
    to_encode.update({"exp": expire})
    
    # Encode the data into a JWT token using the secret key and signing algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Return the encoded JWT token as a string
    return encoded_jwt

# Password related functions

# Function to verify a plain password against the stored hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Use the CryptContext instance to verify if the plain password matches the hashed one
    return pwd_context.verify(plain_password, hashed_password)

# Function to hash a plain password
def get_password_hash(password: str) -> str:
    # Hash the plain password using the CryptContext instance and the bcrypt algorithm
    return pwd_context.hash(password)

# Function to authenticate a developer by checking their username and password
def authenticate_developer(db: Session, username: str, password: str):
    # Retrieve the developer user object from the database based on the username
    user = crud.get_developer(db, "username", username)
    
    # Check if the user exists and if the password matches the hashed password in the database
    if not user or not verify_password(password, user.hashed_password):
        # Return False if authentication fails (either user not found or incorrect password)
        return False
    # Return the user object if authentication is successful
    return user

# Function to authenticate an employer by checking their username and password
def authenticate_employer(db: Session, username: str, password: str):
    # Retrieve the employer user object from the database based on the username
    user = crud.get_employer(db, "username", username)
    
    # Check if the user exists and if the password matches the hashed password in the database
    if not user or not verify_password(password, user.hashed_password):
        # Return False if authentication fails (either user not found or incorrect password)
        return False
    # Return the user object if authentication is successful
    return user

# Getting current developer using access token
async def get_current_developer(token: Annotated[str, Depends(oauth2_scheme_developer)], db: Session = Depends(database.get_db)):
    # Creating an exception for future use when credentials can't be validated
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, # Unauthorized status code
        detail="Could not validate credentials",  # Error message for failed authentication
        headers={"WWW-Authenticate": "Bearer"},   # Header indicating the type of authentication expected
    )
    try:
        # Decode the JWT token and validate its contents
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the username from the payload (this should be stored in the "sub" field of the token)
        username: str = payload.get("sub")
        
        # If there is no username in the token payload, raise the credentials_exception
        if username is None:
            raise credentials_exception
        
        # sch1zk: The official docs create this "useless" variable (token_data) as part of the JWT processing.
        # It's not needed for this function, but it could be useful if the token contained more information.
        token_data = TokenData(username=username)
    except InvalidTokenError:
        # If the token is invalid or has expired, raise the credentials_exception
        raise credentials_exception
    
    # Use a function from the CRUD operations file (crud.py) to fetch the developer by their username
    user = crud.get_developer(db, "username", username)
    
    # If the user is not found in the database, raise the credentials_exception
    if user is None:
        raise credentials_exception
    
    # Return the authenticated developer user object
    return user

# Getting current employer using access token
async def get_current_employer(token: Annotated[str, Depends(oauth2_scheme_employer)], db: Session = Depends(database.get_db)):
    # Creating an exception for future use when credentials can't be validated
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, # Unauthorized status code
        detail="Could not validate credentials",  # Error message for failed authentication
        headers={"WWW-Authenticate": "Bearer"},   # Header indicating the type of authentication expected
    )
    try:
        # Decode the JWT token and validate its contents
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the username from the payload (this should be stored in the "sub" field of the token)
        username: str = payload.get("sub")
        
        # If there is no username in the token payload, raise the credentials_exception
        if username is None:
            raise credentials_exception
        
        # sch1zk: The official docs create this "useless" variable (token_data) as part of the JWT processing.
        # It's not needed for this function, but it could be useful if the token contained more information.
        token_data = TokenData(username=username)
    except InvalidTokenError:
        # If the token is invalid or has expired, raise the credentials_exception
        raise credentials_exception
    
    # Use a function from the CRUD operations file (crud.py) to fetch the employer by their username
    user = crud.get_employer(db, "username", username)
    
    # If the user is not found in the database, raise the credentials_exception
    if user is None:
        raise credentials_exception
    
    # Return the authenticated employer user object
    return user
