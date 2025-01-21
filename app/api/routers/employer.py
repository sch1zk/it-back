from typing import Annotated, List
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app import auth, crud, database, models, schemas

router = APIRouter()

@router.post("/register/", response_model=schemas.Token)
def register(user: schemas.EmployerCreate, db: Session = Depends(database.get_db)):
    # Checking if the username is already registered in the database
    if crud.get_employer(db, "username", user.username):
        # If the username is already in use, raise an HTTPException with a 400 status code
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username '{user.username}' is already registered")
    
    # Checking if the email is already registered in the database
    if crud.get_employer(db, "email", user.email):
        # If the email is already in use, raise an HTTPException with a 400 status code
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{user.email}' is already registered")

    # Creating the developer user in the database
    # The `crud.create_developer` function will create a new developer record and return a success response
    if crud.create_employer(db=db, user=user):
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
    user = auth.authenticate_employer(db, form_data.username, form_data.password)
    
    # If authentication fails (user is not found or password is incorrect), raise an exception
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If authentication is successful, create an access token for the user
    # The 'sub' (subject) in the token payload stores the username
    access_token = auth.create_access_token(
        data={"sub": form_data.username}
    )

    # Return the generated token as part of the response
    # The response model `schemas.Token` includes both the `access_token` and the `token_type` ("bearer")
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/tasks/", response_model=schemas.TaskCreate)
def create_task(
        task_create: schemas.TaskCreate,  # The task creation data passed in the request body
        db: Session = Depends(database.get_db),  # Dependency to provide the database session
        employer: models.UserEmployer = Depends(auth.get_current_employer)  # Dependency to get the current logged-in employer
    ):
    # Creating a new Task instance using the provided task creation data and the employer's ID
    task = models.Task(**task_create.model_dump(), employer_id=employer.id)
    
    # Using the CRUD function to add the task to the database
    result = crud.add_task(db=db, task=task)
    
    # If the task could not be added (result is None), raise a 500 Internal Server Error with an appropriate message
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
    
    # If the task is successfully added, return the created task as the response
    return result

# Route for retrieving a list of tasks, with optional filtering, pagination, and access control
@router.get("/tasks/", response_model=List[schemas.Task])
def get_tasks(
        skip: int = 0,     # Parameter for defining how many tasks to skip (for pagination)
        limit: int = 10,   # Parameter for defining how many tasks to show (for pagination)
        all: bool = False, # If True, the endpoint returns all tasks without pagination
        db: Session = Depends(database.get_db),  # Dependency for database session
        employer: models.UserEmployer = Depends(auth.get_current_employer)  # Dependency for the current authenticated employer
    ):
    # Fetch tasks by employer ID, applying pagination (skip, limit), and optionally returning all tasks
    tasks = crud.get_tasks_by_employer(db, employer.id, skip, limit, all)
    
    # If no tasks were found, raise a 404 error
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found")
    
    # Return the list of tasks
    return tasks

# Route for retrieving a specific task by task_id
@router.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task(
        task_id: int,  # The task ID that we want to retrieve
        db: Session = Depends(database.get_db),  # Dependency for database session
        employer: models.UserEmployer = Depends(auth.get_current_employer)  # Dependency for the current authenticated employer
    ):
    # Fetch the task by its ID from the database
    task = crud.get_task(db, task_id)
    
    # If no task is found, raise a 404 error indicating the task was not found
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Check if the current authenticated employer is the one who created the task
    if employer.id != task.employer_id:
        # If the employer is not the one who created the task, raise a 403 error (Forbidden)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this task")
    
    # Return the task if the employer is authorized to view it
    return task
