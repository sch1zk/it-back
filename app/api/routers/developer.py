from typing import Annotated
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, constr

from app import auth, crud, database, models, schemas

router = APIRouter()

@router.post("/register/", response_model=schemas.Token)
def register(user: schemas.DeveloperCreate, db: Session = Depends(database.get_db)):
    # Validate username and email
    if not isinstance(user.username, str) or not user.username.isalnum():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username format")
    if not isinstance(user.email, str) or not EmailStr.validate(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
    
    # Check if the username is already registered
    if crud.get_developer(db, "username", user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username '{user.username}' is already registered")
    
    # Check if the email is already registered
    if crud.get_developer(db, "email", user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{user.email}' is already registered")

    # Create the developer user
    if crud.create_developer(db=db, user=user):
        access_token = auth.create_access_token(data={"sub": user.username})
        return schemas.Token(access_token=access_token, token_type="bearer")

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(database.get_db)
    ) -> schemas.Token:
    
    # Authenticate the user
    user = auth.authenticate_developer(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": form_data.username})
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/tasks/{task_id}/react/", response_model=schemas.TaskReactionCreate)
def create_reaction(
        task_id: int,
        reaction_create: schemas.TaskReactionCreate,
        db: Session = Depends(database.get_db),
        developer: models.UserDeveloper = Depends(auth.get_current_developer)
    ):

    # Check if the task exists
    if not crud.get_task(db, task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task not found")
    
    # Check if the developer has already reacted
    if crud.is_developer_reacted(db, task_id, developer.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Already reacted to this task")

    # Create a TaskReaction instance
    reaction = models.TaskReaction(**reaction_create.model_dump(), task_id=task_id, developer_id=developer.id)
    
    # Add the reaction to the database
    result = crud.add_reaction(db=db, reaction=reaction)
    
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")
    
    return result

@router.put("/profile/", response_model=schemas.Developer)
def update_profile(
        user_update: schemas.DeveloperUpdate,
        db: Session = Depends(database.get_db),
        developer: models.UserDeveloper = Depends(auth.get_current_developer)
    ):
    # Check if the email is already registered by another user
    if user_update.email and crud.get_developer(db, "email", user_update.email) and user_update.email != developer.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{user_update.email}' is already registered")

    # Update the developer profile
    updated_developer = crud.update_developer(db=db, developer_id=developer.id, user_update=user_update)
    
    if not updated_developer:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")
    
    return updated_developer


