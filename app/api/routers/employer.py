from typing import Annotated, List
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app import auth, crud, database, models, schemas

router = APIRouter()

@router.post("/register/", response_model=schemas.Token)
def register(user: schemas.EmployerCreate, db: Session = Depends(database.get_db)):
    # Check if the username is already registered
    if crud.get_employer(db, "username", user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username '{user.username}' is already registered")
    
    # Check if the email is already registered
    if crud.get_employer(db, "email", user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{user.email}' is already registered")

    # Create the employer user
    if crud.create_employer(db=db, user=user):
        access_token = auth.create_access_token(data={"sub": user.username})
        return schemas.Token(access_token=access_token, token_type="bearer")

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(database.get_db)
    ) -> schemas.Token:

    # Authenticate the user
    user = auth.authenticate_employer(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": form_data.username})
    return schemas.Token(access_token=access_token, token_type="bearer")

@router.post("/tasks/", response_model=schemas.TaskCreate)
def create_task(
        task_create: schemas.TaskCreate,
        db: Session = Depends(database.get_db),
        employer: models.UserEmployer = Depends(auth.get_current_employer)
    ):
    # Create a new Task instance
    task = models.Task(**task_create.model_dump(), employer_id=employer.id)
    
    # Add the task to the database
    result = crud.add_task(db=db, task=task)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )
    
    return result

@router.get("/tasks/", response_model=List[schemas.Task])
def get_tasks(
        skip: int = 0,
        limit: int = 10,
        all: bool = False,
        db: Session = Depends(database.get_db),
        employer: models.UserEmployer = Depends(auth.get_current_employer)
    ):
    # Fetch tasks by employer ID
    tasks = crud.get_tasks_by_employer(db, employer.id, skip, limit, all)
    
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found")
    
    return tasks

@router.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task(
        task_id: int,
        db: Session = Depends(database.get_db),
        employer: models.UserEmployer = Depends(auth.get_current_employer)
    ):
    # Fetch the task by its ID
    task = crud.get_task(db, task_id)
    
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Check if the current employer is the one who created the task
    if employer.id != task.employer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this task")
    
    return task
