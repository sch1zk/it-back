# models.py describes all the data models that reflect the structure of the tables in the database
# This file allows you to create Python objects that correspond to the tables in the database and define the fields of these tables

from sqlalchemy import Column, ForeignKey, Integer, String, Date, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base model, from which all other models will be inherited
Base = declarative_base()

task_dev_association = Table(
    'task_dev_association', Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('developer_id', Integer, ForeignKey('users_dev.id'), primary_key=True)
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

    tasks = relationship('Task', secondary=task_dev_association, back_populates='developers')

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

    tasks = relationship("Task", back_populates="employer")

class Task(Base):
    # Defining how table will be named in the database
    __tablename__ = "tasks"

    # Defining what columns will be used in the database
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)

    employer_id = Column(Integer, ForeignKey("users_emp.id"), nullable=False)
    employer = relationship("UserEmployer", back_populates="tasks")
    developers = relationship("UserDeveloper", secondary=task_dev_association, back_populates="tasks")