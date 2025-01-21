import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
from app import auth, models, schemas

# Set up a logger for this module, using the module's name as the logger's name.
# This helps in distinguishing logs coming from different parts of the application.
# The logger will capture logs at the level defined in the logging configuration.
logger = logging.getLogger(__name__)


# ----- DEVELOPER -----

# Function to get a developer from the database by a specific field (e.g., username, email)
def get_developer(db: Session, field: str, value: str) -> Optional[models.UserDeveloper]:
    try:
        # Query the database to find a developer whose specified field matches the provided value
        # `getattr` dynamically accesses the attribute (field) of the `UserDeveloper` model
        developer = db.query(models.UserDeveloper).filter(getattr(models.UserDeveloper, field) == value).first()
        
        # If no developer is found, log a warning message
        if developer is None:
            logger.warning(f"Developer with {field} {value} not found")
        
        return developer
    
    except SQLAlchemyError as e:
        # If there's an error during the database query, log the error and raise an exception
        logger.error(f"Error fetching developer with {field} {value}: {e}")
        raise Exception(f"An error occurred while retrieving the developer with {field} {value}")

# Function to create a developer user in the database
def create_developer(db: Session, user: schemas.DeveloperCreate) -> bool:
    try:
        # Converting the user schema to a dictionary to make it compatible with the database model
        user_data = user.model_dump()
        
        # Hashing the password and removing the plain password from the user data
        # This ensures the password is securely stored in the database
        user_data["hashed_password"] = auth.pwd_context.hash(user_data.pop("password"))

        # Unpacking the user data dictionary into the UserDeveloper model
        db_user = models.UserDeveloper(**user_data)

        # Adding the user model to the session, committing it to the database, and refreshing the model 
        # to reflect any changes made (like database-generated fields)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # If everything is successful, return True to indicate the user was created
        return True
    except SQLAlchemyError as e:
        # Catching database-related errors (e.g., connection issues, invalid queries)
        logger.error(f"Database error occurred while creating user (developer): {e}")
        db.rollback()  # Rolling back the transaction to prevent partial database writes
        return False  # Returning False if an error occurred during the process
    except Exception as e:
        # Catching any other unexpected errors (e.g., logic errors)
        logger.error(f"Unexpected error occurred while creating user (developer): {e}")
        db.rollback()  # Rolling back the transaction in case of unexpected errors
        return False  # Returning False to indicate failure


# ----- EMPLOYER -----

# Function to retrieve an employer from the database using a specified field and value
def get_employer(db: Session, field: str, value: str) -> Optional[models.UserEmployer]:
    try:
        # Query the database for the employer where the specified field matches the value
        # The 'getattr' function allows for dynamic field selection (e.g., "username", "email")
        employer = db.query(models.UserEmployer).filter(getattr(models.UserEmployer, field) == value).first()

        # If no employer is found, log a warning message with the details of the field and value
        if employer is None:
            logger.warning(f"Employer with {field} {value} not found")
        
        # Return the employer if found, otherwise None
        return employer
    except SQLAlchemyError as e:
        # Catching database-related errors (e.g., query issues, connection problems)
        # Log the error along with the field and value used in the query for debugging
        logger.error(f"Error fetching employer with {field} {value}: {e}")
        
        # Raise a general exception to notify the caller of the failure
        raise Exception(f"An error occurred while retrieving the employer with {field} {value}")

# Function to create an employer in the database
def create_employer(db: Session, user: schemas.EmployerCreate) -> bool:
    try:
        # Convert the 'EmployerCreate' schema to a dictionary to process data
        # This step prepares the schema data to be inserted into the database
        user_data = user.model_dump()

        # Hash the password before storing it in the database
        # The password is popped from the dictionary and hashed using CryptContext
        # The hashed password is then added to the dictionary under the key "hashed_password"
        user_data["hashed_password"] = auth.pwd_context.hash(user_data.pop("password"))

        # Unpack the dictionary to create an instance of the UserEmployer model
        # This model will represent the employer's data in the database
        db_user = models.UserEmployer(**user_data)

        # Add the employer model to the session and commit the changes to the database
        db.add(db_user)
        db.commit()  # Commit the transaction to persist data
        db.refresh(db_user)  # Refresh the instance to update any fields set by the DB (e.g., auto-generated fields)

        # Return True indicating that the employer was successfully created and added to the database
        return True
    except SQLAlchemyError as e:
        # If a SQLAlchemy error occurs, log the error message with details
        logger.error(f"Database error occurred while creating user (employer): {e}")
        
        # Rollback the transaction to ensure the database remains in a consistent state
        db.rollback()

        # Return False to indicate that the employer creation failed
        return False
    except Exception as e:
        # If any other unexpected error occurs, log the error message
        logger.error(f"Unexpected error occurred while creating user (employer): {e}")
        
        # Rollback the transaction to ensure that partial changes are not persisted
        db.rollback()

        # Return False to indicate that an error occurred during employer creation
        return False


# ----- TASK -----

# Function to retrieve a task from the database by its ID
def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    try:
        # Query the Task model and filter by the task ID
        # .first() is used to return the first match or None if no task is found
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        
        # If no task is found, log a warning with the task ID
        if task is None:
            logger.warning(f"Task with id {task_id} not found")
        
        # Return the task object (if found), or None if no task was found
        return task
    except SQLAlchemyError as e:
        # If there's a SQLAlchemy-specific error (e.g., connection issues, invalid query), log the error with details
        logger.error(f"Error fetching task with id {task_id}: {e}")
        
        # Raise a generic exception indicating a database retrieval error, passing the task ID in the error message
        raise Exception(f"An error occurred while retrieving the task with id {task_id}")

# Function to retrieve all tasks for a specific employer from the database
def get_tasks_by_employer(
            db: Session,            # Database session
            employer_id: int,       # ID of the employer to fetch tasks for
            skip: int = 0,          # Number of tasks to skip (for pagination)
            limit: int = 10,        # Maximum number of tasks to return (for pagination)
            all: bool = False       # Flag to indicate if all tasks should be fetched (bypassing pagination)
        ) -> List[models.Task]:
    try:
        # If 'all' is True, return all tasks for the given employer, without pagination
        if all:
            return db.query(models.Task).filter(models.Task.employer_id == employer_id).all()
        
        # Otherwise, apply pagination by skipping 'skip' number of tasks and limiting to 'limit' number of tasks
        return db.query(models.Task).filter(models.Task.employer_id == employer_id).offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        # Log error if there's an issue fetching the tasks from the database
        logger.error(f"Error fetching tasks from employer with id {employer_id}: {e}")
        
        # Raise a generic exception to indicate an error occurred while retrieving tasks
        raise Exception(f"An error occurred while retrieving the tasks from employer with id {employer_id}")

# Function to check if a developer has already reacted to a task
def is_developer_reacted(db: Session, task_id: int, developer_id: int) -> bool:
    try:
        # Use scalar() to check if a reaction exists for the given task and developer
        # The filter_by method is used to apply the filters directly to the query (task_id and developer_id)
        # scalar() will return the first result of the query or None if no matching record is found
        return db.query(models.TaskReaction).filter_by(task_id=task_id, developer_id=developer_id).scalar() is not None

    except SQLAlchemyError as e:
        # Log the error in case of an issue during the database query
        logger.error(f"Database error occurred while checking reaction: {e}")

        # Raise a generic exception with a message, indicating the task retrieval failure
        raise Exception(f"An error occurred while retrieving the task with id {task_id}")

# Function to add a new task to the database
def add_task(db: Session, task: models.Task) -> Optional[models.Task]:
    try:
        # Add the task to the session, preparing it to be committed to the database
        db.add(task)

        # Commit the transaction to save the task into the database
        db.commit()

        # Refresh the task object to ensure it contains the most up-to-date data from the database (e.g., auto-generated fields like ID)
        db.refresh(task)

        # Return the task object back to the caller, as it has been successfully added to the database
        # This can be easily modified later if needed (e.g., returning a different object or data)
        return task

    except SQLAlchemyError as e:
        # Log the error message if a database-specific issue occurs (e.g., SQL error, connection failure)
        logger.error(f"Database error occurred while adding task: {e}")

        # Rollback the transaction to avoid leaving partial changes in the database in case of an error
        db.rollback()

    except Exception as e:
        # Log unexpected errors (e.g., logic errors, unexpected failures)
        logger.error(f"Unexpected error occurred while adding task: {e}")

        # Rollback the transaction to maintain database integrity
        db.rollback()


# ----- TASK REACTION -----

# Function to get task reaction by its id from the database
def get_reaction(db: Session, task_id: int) -> Optional[models.TaskReaction]:
    try:
        # Query the TaskReaction table to find a reaction that matches the given task_id
        reaction = db.query(models.TaskReaction).filter(models.TaskReaction.id == task_id).first()

        # If no reaction is found, log a warning and return None
        if reaction is None:
            logger.warning(f"Task reaction with id {task_id} not found")

        # Return the found reaction, or None if not found
        return reaction
    except SQLAlchemyError as e:
        # Log any SQLAlchemy-specific errors (e.g., connection issue, query issue) that may occur during the query
        logger.error(f"Error fetching task reaction with id {task_id}: {e}")
        # Raise a general exception with a descriptive message
        raise Exception(f"An error occurred while retrieving the task reaction with id {task_id}")

# Function to add a new task reaction to the database
def add_reaction(db: Session, reaction: models.TaskReaction) -> Optional[models.TaskReaction]:
    try:
        # Add the reaction to the session, preparing it for commit to the database
        db.add(reaction)

        # Commit the transaction to save the reaction to the database
        db.commit()

        # Refresh the reaction object to ensure it contains the latest data from the database
        db.refresh(reaction)

        # Return the reaction object back to the caller, as it has been successfully added to the database
        return reaction
    except SQLAlchemyError as e:
        # Log any database-specific errors (e.g., SQL errors, connection issues)
        logger.error(f"Database error occurred while adding reaction: {e}")
        # Rollback the transaction in case of an error to maintain database integrity
        db.rollback()
    except Exception as e:
        # Log unexpected errors that may occur during the reaction creation
        logger.error(f"Unexpected error occurred while adding reaction: {e}")
        # Rollback the transaction to ensure no partial data is committed to the database
        db.rollback()


