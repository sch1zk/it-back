# crud.py is a storage for funcs that perform database operations

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from app import models, schemas

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----- DEVELOPER -----

# Getting user from database
def get_developer(db: Session, field: str, value: str) -> Optional[models.UserDeveloper]:
    try:
        developer = db.query(models.UserDeveloper).filter(getattr(models.UserDeveloper, field) == value).first()
        if developer is None:
            logger.warning(f"Developer with {field} {value} not found")
        return developer
    except SQLAlchemyError as e:
        logger.error(f"Error fetching developer with {field} {value}: {e}")
        raise Exception(f"An error occurred while retrieving the developer with {field} {value}")

# Creating user in database
def create_developer(db: Session, user: schemas.DeveloperCreate) -> bool:
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
        logger.error(f"Database error occurred while creating user (developer): {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating user (developer): {e}")
        db.rollback()
        return False

# ----- EMPLOYER -----

# Getting user from database
def get_employer(db: Session, field: str, value: str) -> Optional[models.UserEmployer]:
    try:
        employer = db.query(models.UserEmployer).filter(getattr(models.UserEmployer, field) == value).first()
        if employer is None:
            logger.warning(f"Employer with {field} {value} not found")
        return employer
    except SQLAlchemyError as e:
        logger.error(f"Error fetching employer with {field} {value}: {e}")
        raise Exception(f"An error occurred while retrieving the employer with {field} {value}")

# Creating user in database
def create_employer(db: Session, user: schemas.EmployerCreate) -> bool:
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
        logger.error(f"Database error occurred while creating user (employer): {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating user (employer): {e}")
        db.rollback()
        return False

# ----- TASK -----

# Getting task by its id from database
def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if task is None:
            logger.warning(f"Task with id {task_id} not found")
        return task
    except SQLAlchemyError as e:
        logger.error(f"Error fetching task with id {task_id}: {e}")
        raise Exception(f"An error occurred while retrieving the task with id {task_id}")

# Getting all tasks by employer id from database
def get_tasks_by_employer(
            db: Session,
            employer_id: int,
            skip: int = 0,
            limit: int = 10,
            all: bool = False
        ) -> List[models.Task]:
    try:
        if all:
            return db.query(models.Task).filter(models.Task.employer_id == employer_id).all()
        return db.query(models.Task).filter(models.Task.employer_id == employer_id).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching tasks from employer with id {employer_id}: {e}")
        raise Exception(f"An error occurred while retrieving the tasks from employer with id {employer_id}")

# Checking is developer already reacted to task
def is_developer_reacted(db: Session, task_id: int, developer_id: int) -> bool:
    try:
        # Check for developer reaction directly with scalar
        return db.query(models.TaskReaction).filter_by(task_id=task_id, developer_id=developer_id).scalar() is not None
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while checking reaction: {e}")
        raise Exception(f"An error occurred while retrieving the task with id {task_id}")

# Creating task in database
def add_task(db: Session, task: models.Task) -> Optional[models.Task]:
    try:
        db.add(task)
        db.commit()
        db.refresh(task)

        # Returning Task back to user for now, can be easily changed later
        return task
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while adding task: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Unexpected error occurred while adding task: {e}")
        db.rollback()

# ----- TASK REACTION -----

# Getting task reaction by its id from database
def get_reaction(db: Session, task_id: int) -> Optional[models.TaskReaction]:
    try:
        reaction = db.query(models.TaskReaction).filter(models.TaskReaction.id == task_id).first()
        if reaction is None:
            logger.warning(f"Task reaction with id {task_id} not found")
        return reaction
    except SQLAlchemyError as e:
        logger.error(f"Error fetching task reaction with id {task_id}: {e}")
        raise Exception(f"An error occurred while retrieving the task reaction with id {task_id}")

# Creating task reaction in database
def add_reaction(db: Session, reaction: models.TaskReaction) -> Optional[models.TaskReaction]:
    try:
        db.add(reaction)
        db.commit()
        db.refresh(reaction)

        # Returning TaskReaction back to user for now, can be easily changed later
        return reaction
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while adding reaction: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Unexpected error occurred while adding reaction: {e}")
        db.rollback()

