from typing import Annotated
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app import auth, crud, database, models, schemas

router = APIRouter()

@router.post("/register/", response_model=schemas.Token)
def register(user: schemas.DeveloperCreate, db: Session = Depends(database.get_db)):
    # Checking if the username is already registered in the database
    if crud.get_developer(db, "username", user.username):
        # If the username is already in use, raise an HTTPException with a 400 status code
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username '{user.username}' is already registered")
    
    # Checking if the email is already registered in the database
    if crud.get_developer(db, "email", user.email):
        # If the email is already in use, raise an HTTPException with a 400 status code
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{user.email}' is already registered")

    # Creating the developer user in the database
    # The `crud.create_developer` function will create a new developer record and return a success response (bool)
    if crud.create_developer(db=db, user=user):
        # If user creation is successful, generate an access token for the newly created user
        access_token = auth.create_access_token(
            data={"sub": user.username}  # The 'sub' field in the JWT payload stores the username
        )
        # Return the generated token wrapped in a response model (`schemas.Token`)
        return schemas.Token(access_token=access_token, token_type="bearer")

    # If there is an unexpected error and the user could not be created, raise an HTTPException with a 500 status code
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(database.get_db)
    ) -> schemas.Token:
    
    # Authenticate the user by verifying the username and password
    # This calls the `authenticate_developer` function from the auth module to validate credentials
    user = auth.authenticate_developer(db, form_data.username, form_data.password)
    
    # If authentication fails (user is not found or password is incorrect), raise an exception
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # 401 indicates unauthorized access
            detail="Incorrect username or password",  # Message to send to the client
            headers={"WWW-Authenticate": "Bearer"},  # This header tells the client that the endpoint expects a Bearer token
        )

    # If authentication is successful, create an access token for the user
    # The 'sub' (subject) in the token payload stores the username
    access_token = auth.create_access_token(
        data={"sub": form_data.username}  # The data field includes the username
    )
    
    # Return the generated token as part of the response
    # The response model `schemas.Token` includes both the `access_token` and the `token_type` ("bearer")
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/tasks/{task_id}/react/", response_model=schemas.TaskReactionCreate)
def create_reaction(
        task_id: int,  # The ID of the task that the developer is reacting to
        reaction_create: schemas.TaskReactionCreate,  # The reaction data provided by the developer
        db: Session = Depends(database.get_db),  # Dependency that provides the database session
        developer: models.UserDeveloper = Depends(auth.get_current_developer)  # Dependency that retrieves the current logged-in developer
    ):

    # Check if the task with the given task_id exists
    if not crud.get_task(db, task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task not found")  # Raise 404 if task is not found
    
    # Check if the developer has already reacted to this task
    if crud.is_developer_reacted(db, task_id, developer.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Already reacted to this task")  # Raise 400 if developer has already reacted to this task

    # Create a TaskReaction model instance using the data provided in the request body
    reaction = models.TaskReaction(**reaction_create.model_dump(), task_id=task_id, developer_id=developer.id)
    
    # Add the reaction to the database and get the result
    result = crud.add_reaction(db=db, reaction=reaction)
    
    # If the reaction wasn't successfully added, raise an exception
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")  # Raise 500 if something went wrong with adding the reaction
    
    # Return the created reaction as the response
    return result

    
    