# models.py describes all the data models that reflect the structure of the tables in the database
# This file allows you to create Python objects that correspond to the tables in the database and define the fields of these tables

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base model, from which all other models will be inherited
Base = declarative_base()

developer_task_association = Table(
    'developer_task_association', Base.metadata,
    Column('developer_id', Integer, ForeignKey('users_dev.id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True)
)

class UserDeveloper(Base):
    # Defining how table will be named in the database
    __tablename__ = "users_dev"

    # Defining what columns will be used in the database
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Developer info
    first_name = Column(String)
    second_name = Column(String)
    middle_name = Column(String)
    birth_date = Column(Date)
    city = Column(String)
    phone_number = Column(String)

    # Relationships with other tables
    assigned_tasks = relationship('Task', secondary=developer_task_association, back_populates='assigned_developers')
    tasks_reactions = relationship("TaskReaction", back_populates="developer")

class UserEmployer(Base):
    # Defining how table will be named in the database
    __tablename__ = "users_emp"

    # Defining what columns will be used in the database
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Employer info
    company_name = Column(String)

    # Relationships with other tables
    created_tasks = relationship("Task", back_populates="employer")

class Task(Base):
    # Defining how table will be named in the database
    __tablename__ = "tasks"

    # Defining what columns will be used in the database
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)

    # Relationships with other tables
    employer_id = Column(Integer, ForeignKey("users_emp.id"), nullable=False)
    employer = relationship("UserEmployer", back_populates="created_tasks")

    reactions = relationship('TaskReaction', back_populates='task')
    assigned_developers = relationship('UserDeveloper', secondary=developer_task_association, back_populates='assigned_tasks')

class TaskReaction(Base):
    # Defining how table will be named in the database
    __tablename__ = "tasks_reactions"

    # Defining what columns will be used in the database
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(Text)

    # Relationships with other tables
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="reactions")

    developer_id = Column(Integer, ForeignKey("users_dev.id"))
    developer = relationship("UserDeveloper", back_populates="tasks_reactions")