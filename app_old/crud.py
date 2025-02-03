import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app import auth, models, schemas

logger = logging.getLogger(__name__)

# ----- DEVELOPER -----

def get_developer(db: Session, field: str, value: str) -> Optional[models.UserDeveloper]:
    try:
        developer = db.query(models.UserDeveloper).filter(getattr(models.UserDeveloper, field) == value).first()
        if developer is None:
            logger.warning(f"Developer with {field} {value} not found")
        return developer
    except SQLAlchemyError as e:
        logger.error(f"Error fetching developer with {field} {value}: {e}")
        raise Exception(f"An error occurred while retrieving the developer with {field} {value}")

def create_developer(db: Session, user: schemas.DeveloperCreate) -> bool:
    try:
        user_data = user.model_dump()
        user_data["hashed_password"] = auth.pwd_context.hash(user_data.pop("password"))
        db_user = models.UserDeveloper(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return True
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while creating user (developer): {e}")
        db.rollback()
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while creating user (developer): {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating user (developer): {e}")
        db.rollback()
        return False

def update_developer(db: Session, developer_id: int, user_update: schemas.DeveloperUpdate) -> Optional[models.UserDeveloper]:
    try:
        developer = db.query(models.UserDeveloper).filter(models.UserDeveloper.id == developer_id).first()
        if not developer:
            logger.warning(f"Developer with id {developer_id} not found")
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(developer, key, value)
        
        db.commit()
        db.refresh(developer)
        return developer
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while updating developer with id {developer_id}: {e}")
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error occurred while updating developer with id {developer_id}: {e}")
        db.rollback()
        return None

# ----- EMPLOYER -----

def get_employer(db: Session, field: str, value: str) -> Optional[models.UserEmployer]:
    try:
        employer = db.query(models.UserEmployer).filter(getattr(models.UserEmployer, field) == value).first()
        if employer is None:
            logger.warning(f"Employer with {field} {value} not found")
        return employer
    except SQLAlchemyError as e:
        logger.error(f"Error fetching employer with {field} {value}: {e}")
        raise Exception(f"An error occurred while retrieving the employer with {field} {value}")

def create_employer(db: Session, user: schemas.EmployerCreate) -> bool:
    try:
        user_data = user.model_dump()
        user_data["hashed_password"] = auth.pwd_context.hash(user_data.pop("password"))
        db_user = models.UserEmployer(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return True
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while creating user (employer): {e}")
        db.rollback()
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while creating user (employer): {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating user (employer): {e}")
        db.rollback()
        return False

# ----- TASK -----

def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if task is None:
            logger.warning(f"Task with id {task_id} not found")
        return task
    except SQLAlchemyError as e:
        logger.error(f"Error fetching task with id {task_id}: {e}")
        raise Exception(f"An error occurred while retrieving the task with id {task_id}")

def get_tasks_by_employer(db: Session, employer_id: int, skip: int = 0, limit: int = 10, all: bool = False) -> List[models.Task]:
    try:
        if all:
            return db.query(models.Task).filter(models.Task.employer_id == employer_id).all()
        return db.query(models.Task).filter(models.Task.employer_id == employer_id).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching tasks from employer with id {employer_id}: {e}")
        raise Exception(f"An error occurred while retrieving the tasks from employer with id {employer_id}")

def is_developer_reacted(db: Session, task_id: int, developer_id: int) -> bool:
    try:
        return db.query(models.TaskReaction).filter_by(task_id=task_id, developer_id=developer_id).scalar() is not None
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while checking reaction: {e}")
        raise Exception(f"An error occurred while retrieving the task with id {task_id}")

def add_task(db: Session, task: models.Task) -> Optional[models.Task]:
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while adding task: {e}")
        db.rollback()
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while adding task: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Unexpected error occurred while adding task: {e}")
        db.rollback()

# ----- TASK REACTION -----

def get_reaction(db: Session, task_id: int) -> Optional[models.TaskReaction]:
    try:
        reaction = db.query(models.TaskReaction).filter(models.TaskReaction.id == task_id).first()
        if reaction is None:
            logger.warning(f"Task reaction with id {task_id} not found")
        return reaction
    except SQLAlchemyError as e:
        logger.error(f"Error fetching task reaction with id {task_id}: {e}")
        raise Exception(f"An error occurred while retrieving the task reaction with id {task_id}")

def add_reaction(db: Session, reaction: models.TaskReaction) -> Optional[models.TaskReaction]:
    try:
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        return reaction
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while adding reaction: {e}")
        db.rollback()
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while adding reaction: {e}")
        db.rollback()
    except Exception as e:
        logger.error(f"Unexpected error occurred while adding reaction: {e}")
        db.rollback()


