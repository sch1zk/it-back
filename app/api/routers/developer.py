from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import auth, crud, database, models, schemas

router = APIRouter()

@router.post("/register/", response_model=schemas.Token)
def register(user: schemas.DeveloperCreate, db: Session = Depends(database.get_db)) -> schemas.Token:
    # Validate username and email
    if not isinstance(user.username, str) or not user.username.isalnum():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username format")
    # if not isinstance(user.email, str) or not EmailStr.validate(user.email):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
    
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


@router.get("/tasks/", response_model=List[schemas.Task])
def get_tasks(
    skip: int = 0,
    limit: int = 10,
    all: bool = False,
    db: Session = Depends(database.get_db),
    developer: models.UserDeveloper = Depends(auth.get_current_developer)
):
    # Fetch tasks
    tasks = crud.get_tasks(db, skip, limit, all)
    
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found"
        )
    
    return tasks

@router.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task(
    task_id: int,
    db: Session = Depends(database.get_db),
    developer: models.UserDeveloper = Depends(auth.get_current_developer)
):
    # Fetch the task by its ID
    task = crud.get_task(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task

@router.post("/tasks/{task_id}/react/", response_model=schemas.TaskReactionCreate)
def create_reaction(
    task_id: int,
    reaction_create: schemas.TaskReactionCreate,
    db: Session = Depends(database.get_db),
    developer: models.UserDeveloper = Depends(auth.get_current_developer)
) -> schemas.TaskReactionCreate:
    # Check if the task exists
    if not crud.get_task(db, task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Check if the developer has already reacted
    if crud.is_developer_reacted(db, task_id, developer.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already reacted to this task")

    # Create a TaskReaction instance
    reaction = models.TaskReaction(**reaction_create.model_dump(), task_id=task_id, developer_id=developer.id)
    
    # Add the reaction to the database
    result = crud.add_reaction(db=db, reaction=reaction)
    
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")
    
    return result

@router.get("/profile/", response_model=schemas.DeveloperProfile)
def get_profile(
    db: Session = Depends(database.get_db),
    developer: models.UserDeveloper = Depends(auth.get_current_developer)
):
    achievements = crud.get_achievements(db, developer.id)

    return {
        "username": developer.username,
        "email": developer.email,
        "achievements": [
            {
                "id": achievement.id,
                "developer_id": achievement.developer_id,
                "achievement_id": achievement.achievement_id,
                "achievement": {
                    "id": achievement.achievement.id,
                    "title": achievement.achievement.title,
                    "description": achievement.achievement.description,
                },
                "date_awarded": achievement.date_awarded
            } for achievement in achievements
        ] if achievements else []
    }

@router.put("/profile/", response_model=schemas.Developer)
def update_profile(
    user_update: schemas.DeveloperUpdate,
    db: Session = Depends(database.get_db),
    developer: models.UserDeveloper = Depends(auth.get_current_developer)
) -> schemas.Developer:
    # Check if the email is already registered by another user
    if user_update.email and crud.get_developer(db, "email", user_update.email) and user_update.email != developer.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Email '{user_update.email}' is already registered")

    # Update the developer profile
    updated_developer = crud.update_developer(db=db, developer_id=developer.id, user_update=user_update)
    
    if not updated_developer:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred. Please try again later.")
    
    return updated_developer

@router.get("/skills/", response_model=List[schemas.Skill])
def get_skills(
    db: Session = Depends(database.get_db),
    developer: models.UserDeveloper = Depends(auth.get_current_developer)
) -> List[schemas.Skill]:
    return crud.get_all_skills_templates(db)

@router.post("/profile/skills/")
def add_skill_to_profile(
    skill_id: int,
    db: Session = Depends(database.get_db),
    developer: models.UserDeveloper = Depends(auth.get_current_developer)
):
    if crud.add_skill(db, developer.id, skill_id):
        return {"message": "Skill added successfully"}

@router.get("/profile/skills/", response_model=List[str])
def get_profile_skills(
    db: Session = Depends(database.get_db),
    developer: models.UserDeveloper = Depends(auth.get_current_developer)
) -> List[str]:
    return crud.get_skills(db, developer.id)