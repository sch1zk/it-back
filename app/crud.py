# crud.py is a storage for funcs that perform database operations

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----- DEVELOPER -----

# Getting user by its id from database
def get_developer(db: Session, user_id: int):
    return db.query(models.UserDeveloper).filter(models.UserDeveloper.id == user_id).first()

# Getting user from database by its username
def get_developer_by_username(db: Session, username: str):
    return db.query(models.UserDeveloper).filter(models.UserDeveloper.username == username).first()

# Getting user from database by its email
def get_developer_by_email(db: Session, email: str):
    return db.query(models.UserDeveloper).filter(models.UserDeveloper.email == email).first()

# Creating user in database
def create_developer(db: Session, user: schemas.DeveloperCreate):
    try:
        # Converting schema to dict
        user_data = user.model_dump()
        user_data["hashed_password"] = pwd_context.hash(user_data.pop("password"))

        # Unpacking dict to created user model
        db_user = models.UserDeveloper(**user_data)

        # Sending model to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Return True to "register" in "api.routers.developer" if all is ok
        return True
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        db.rollback()
        return False
    except Exception as e:
        print(f"Unexpected error when creating user (developer): {e}")
        db.rollback()
        return False

# ----- EMPLOYER -----

# Getting user from database by its id
def get_employer(db: Session, user_id: int):
    return db.query(models.UserEmployer).filter(models.UserEmployer.id == user_id).first()

# Getting user from database by its username
def get_employer_by_username(db: Session, username: str):
    return db.query(models.UserEmployer).filter(models.UserEmployer.username == username).first()

# Getting user from database by its email
def get_employer_by_email(db: Session, email: str):
    return db.query(models.UserEmployer).filter(models.UserEmployer.email == email).first()

# Creating user in database
def create_employer(db: Session, user: schemas.EmployerCreate):
    try:
        # Converting schema to dict
        user_data = user.model_dump()
        user_data["hashed_password"] = pwd_context.hash(user_data.pop("password"))

        # Unpacking dict to created user model
        db_user = models.UserEmployer(**user_data)

        # Sending model to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Return True to "register" in "api.routers.employer" if all is ok
        return True
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        db.rollback()
        return False
    except Exception as e:
        print(f"Unexpected error when creating user (employer): {e}")
        db.rollback()
        return False

# ----- TASK -----

# Getting task by its id from database
def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

# Checking is developer already reacted to task
def is_developer_reacted(db: Session, task_id: int, developer_id: int) -> bool:
    reaction_exists = db.query(models.TaskReaction).filter(
        models.TaskReaction.task_id == task_id,
        models.TaskReaction.developer_id == developer_id
    ).first()

    return reaction_exists is not None

# Creating task in database
def add_task(db: Session, task: models.Task):
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        db.rollback()
    except Exception as e:
        print(f"Unexpected error when adding new task to database: {e}")
        db.rollback()

# ----- TASK REACTION -----

# Getting task reaction by its id from database
def get_reaction(db: Session, task_id: int):
    return db.query(models.TaskReaction).filter(models.TaskReaction.id == task_id).first() 

# Creating task reaction in database
def add_reaction(db: Session, reaction: models.TaskReaction):
    try:
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        return reaction
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        db.rollback()
    except Exception as e:
        print(f"Unexpected error when adding new task to database: {e}")
        db.rollback()
