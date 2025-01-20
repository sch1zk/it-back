from typing import Annotated, List
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app import auth, crud, database, models, schemas

router = APIRouter()

@router.post("/register/", response_model=schemas.Token)
def register(user: schemas.EmployerCreate, db: Session = Depends(database.get_db)):
    # Checking is username already registered
    if crud.get_employer(db, "username", user.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Username '{user.username}' is already registered")
    
    # Checking is email already registered
    if crud.get_employer(db, "email", user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{user.email}' is already registered")

    # Creating user (employer) and returning access token if succeeded
    if crud.create_employer(db=db, user=user):
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
    user = auth.authenticate_employer(db, form_data.username, form_data.password)
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

@router.post("/tasks/", response_model=schemas.TaskCreate)
def create_task(
        task_create: schemas.TaskCreate,
        db: Session = Depends(database.get_db),
        employer: models.UserEmployer = Depends(auth.get_current_employer)
    ):
    task = models.Task(**task_create.model_dump(), employer_id=employer.id)
    result = crud.add_task(db=db, task=task)
    if not result:
        # Throwing exception if reaction is not created
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")
    
    return result

def get_tasks_by_employer(db: Session, employer_id: int) -> List[models.Task]:
    return db.query(models.Task).filter(models.Task.employer_id == employer_id).all()

@router.get("/tasks/", response_model=List[schemas.Task])
def get_tasks(
        skip: int = 0,     # Param for defining how many tasks to skip
        limit: int = 10,   # Param for defining how many tasks to show
        all: bool = False, # If True, requests all tasks
        db: Session = Depends(database.get_db),
        employer: models.UserEmployer = Depends(auth.get_current_employer)
    ):
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
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if employer.id != task.employer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this task")

    return task