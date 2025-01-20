from typing import Annotated
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app import auth, crud, database, models, schemas

router = APIRouter()

@router.post("/register/", response_model=schemas.Token)
def register(user: schemas.DeveloperCreate, db: Session = Depends(database.get_db)):
    # Checking is username already registered
    if crud.get_developer_by_username(db, user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username '{user.username}' already registered")
    
    # Checking is email already registered
    if crud.get_developer_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{user.email}' already registered")

    # Creating user (developer) and returning access token if succeeded
    if crud.create_developer(db=db, user=user):
        access_token = auth.create_access_token(
            data={"sub": user.username}
        )
        return schemas.Token(access_token=access_token, token_type="bearer")

    # Throwing exception if user is not created
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(database.get_db)
    ) -> schemas.Token:
    user = auth.authenticate_developer(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": form_data.username}
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/tasks/{task_id}/react/", response_model=schemas.TaskReactionCreate)
def create_reaction(
        task_id: int,
        reaction_create: schemas.TaskReactionCreate,
        db: Session = Depends(database.get_db),
        developer: models.UserDeveloper = Depends(auth.get_current_developer)
    ):
    reaction = models.TaskReaction(**reaction_create.model_dump(), task_id=task_id, developer_id=developer.id)
    return crud.add_reaction(db=db, reaction=reaction)