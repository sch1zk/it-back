# crud.py is a storage for funcs that perform database operations

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----- DEVELOPER -----

# Getting user by its id from database
def get_dev(db: Session, user_id: int):
    return db.query(models.UserDeveloper).filter(models.UserDeveloper.id == user_id).first()

# Getting user by its username from database
def get_dev_by_username(db: Session, username: str):
    return db.query(models.UserDeveloper).filter(models.UserDeveloper.username == username).first()

# Creating user in database
def create_dev(db: Session, user: schemas.DeveloperCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.UserDeveloper(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        second_name=user.second_name,
        middle_name=user.middle_name,
        birth_date=user.birth_date,
        city=user.city,
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ----- EMPLOYER -----

# Getting user by its id from database
def get_emp(db: Session, user_id: int):
    return db.query(models.UserEmployer).filter(models.UserEmployer.id == user_id).first()

# Getting user by its username from database
def get_emp_by_username(db: Session, username: str):
    return db.query(models.UserEmployer).filter(models.UserEmployer.username == username).first()

# Creating user in database
def create_emp(db: Session, user: schemas.EmployerCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.UserEmployer(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        company_name=user.company_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ----- TASK -----

def add_task(db: Session, task: models.Task):
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

# ----- TASK REACTION -----

def add_task_reaction(db: Session, reaction: models.TaskReaction):
    db.add(reaction)
    db.commit()
    db.refresh(reaction)
    return reaction