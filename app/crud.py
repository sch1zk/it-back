# crud.py is a storage for funcs that perform database operations

from sqlalchemy.orm import Session
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
    except Exception as e:
        print(f"Unexpected error when creating user (developer): {e}")
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
    except Exception as e:
        print(f"Unexpected error when creating user (employer): {e}")
        return False

# ----- TASK -----

def add_task(db: Session, task: models.Task):
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

# ----- TASK REACTION -----

def add_reaction(db: Session, reaction: models.TaskReaction):
    db.add(reaction)
    db.commit()
    db.refresh(reaction)
    return reaction