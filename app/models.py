# models.py describes all the data models that reflect the structure of the tables in the database
# This file allows you to create Python objects that correspond to the tables in the database and define the fields of these tables

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

# Base model, from which all other models will be inherited
Base = declarative_base()

class User(Base):
    # Defining how table will be named in the database
    __tablename__ = "users"

    # Defining what columns will be used in the database
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class UserDeveloper(Base):
    # Defining how table will be named in the database
    __tablename__ = "users_dev"

    # Defining what columns will be used in the database
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    first_name = Column(String)
    second_name = Column(String)
    middle_name = Column(String)
    birth_date = Column(Date)
    city = Column(String)
    phone_number = Column(String)

class UserEmployer(Base):
    # Defining how table will be named in the database
    __tablename__ = "users_emp"

    # Defining what columns will be used in the database
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    company_name = Column(String)