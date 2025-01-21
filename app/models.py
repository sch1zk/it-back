from sqlalchemy import Column, ForeignKey, Integer, String, Date, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base model, from which all other models will inherit
# `Base` is used to define the base class for all SQLAlchemy ORM models. 
# All models should inherit from `Base` to automatically create database tables.
Base = declarative_base()

# Defining an association table for many-to-many relationship between developers and tasks
# This table is used to establish a relationship between the 'users_dev' table and the 'tasks' table
# It stores pairs of developer and task IDs to signify the tasks that developers are assigned to.
developer_task_association = Table(
    'developer_task_association', Base.metadata,  # Table name and metadata for the base model
    Column('developer_id', Integer, ForeignKey('users_dev.id'), primary_key=True),  # Developer ID, foreign key to 'users_dev' table
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True)  # Task ID, foreign key to 'tasks' table
)

class UserDeveloper(Base):
    # Defining the table name for this model
    __tablename__ = "users_dev"  # The name of the table in the database for storing developer information

    # Defining the columns for the 'users_dev' table
    id = Column(Integer, primary_key=True, index=True)  # Developer's unique ID (primary key)
    username = Column(String, unique=True, index=True)  # Username, unique and indexed
    email = Column(String, unique=True, index=True)  # Email, unique and indexed
    hashed_password = Column(String)  # Hashed password (to store passwords securely)

    # Additional developer info
    first_name = Column(String)  # First name of the developer
    second_name = Column(String)  # Last name of the developer
    middle_name = Column(String)  # Middle name of the developer (optional)
    birth_date = Column(Date)  # Date of birth
    city = Column(String)  # City where the developer resides
    phone_number = Column(String)  # Developer's contact number

    # Defining relationships with other tables
    # This creates a many-to-many relationship between developers and tasks
    assigned_tasks = relationship('Task', secondary=developer_task_association, back_populates='assigned_developers')
    # The 'assigned_tasks' field links to tasks assigned to the developer via the association table
    
    tasks_reactions = relationship("TaskReaction", back_populates="developer")
    # The 'tasks_reactions' field links to reactions made by the developer on tasks


# The UserEmployer class represents the "users_emp" table in the database.
# This table stores information about employers who create tasks.
class UserEmployer(Base):
    # Defining the name of the table in the database for employers
    __tablename__ = "users_emp"

    # Defining the columns used in the "users_emp" table
    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each employer (primary key)
    username = Column(String, unique=True, index=True)  # Unique username for the employer
    email = Column(String, unique=True, index=True)  # Unique email for the employer
    hashed_password = Column(String)  # Employer's hashed password for secure login

    # Employer-specific information
    company_name = Column(String)  # The name of the company the employer represents

    # Relationships with other tables:
    # Establishing a one-to-many relationship between an employer and the tasks they create
    created_tasks = relationship("Task", back_populates="employer")
    # The employer can create multiple tasks, so each task will have an employer linked to it

# The Task class represents the "tasks" table in the database.
# This table stores information about tasks created by employers.
class Task(Base):
    # Defining the name of the table in the database for tasks
    __tablename__ = "tasks"

    # Defining the columns used in the "tasks" table
    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each task (primary key)
    title = Column(String)  # Title of the task
    description = Column(Text)  # Detailed description of the task

    # Relationships with other tables:
    # Linking each task to the employer who created it using a foreign key (employer_id)
    employer_id = Column(Integer, ForeignKey("users_emp.id"), nullable=False)  # Foreign key to "users_emp"
    employer = relationship("UserEmployer", back_populates="created_tasks")  # Reverse relationship to get the employer

    # Defining relationships to other tables:
    # Each task can have multiple reactions from developers
    reactions = relationship('TaskReaction', back_populates='task')
    # Tasks can be assigned to multiple developers via the many-to-many relationship
    assigned_developers = relationship('UserDeveloper', secondary=developer_task_association, back_populates='assigned_tasks')

# The TaskReaction class represents the "tasks_reactions" table in the database.
# This table stores the reactions made by developers on tasks.
class TaskReaction(Base):
    # Defining the name of the table in the database for task reactions
    __tablename__ = "tasks_reactions"

    # Defining the columns used in the "tasks_reactions" table
    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each task reaction (primary key)
    title = Column(String)  # Title of the reaction
    message = Column(Text)  # Detailed message or content of the reaction

    # Relationships with other tables:
    # Linking the task reaction to the task it is related to via the task_id foreign key
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="reactions")  # Reverse relationship to get the task for this reaction

    # Linking the task reaction to the developer who created it via the developer_id foreign key
    developer_id = Column(Integer, ForeignKey("users_dev.id"))
    developer = relationship("UserDeveloper", back_populates="tasks_reactions")  # Reverse relationship to get the developer
