from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

# ----- USER (PARENT) -----

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    username: str
    email: str | None = None

    class Config:
        orm_mode = True

# Unused?
class UserInDB(User):
    hashed_password: str

# ----- DEVELOPER (CHILD) -----

# Schema for developer /register/
class DeveloperCreate(UserCreate):
    first_name: str
    second_name: str
    middle_name: str
    birth_date: date
    city: str
    phone_number: str

class Developer(User):
    first_name: str
    second_name: str
    middle_name: str | None = None
    birth_date: date | None = None
    city: str | None = None
    phone_number: str | None = None

# Schema for developer update profile
class DeveloperUpdate(BaseModel):
    first_name: str | None = None
    second_name: str | None = None
    middle_name: str | None = None
    birth_date: date | None = None
    city: str | None = None
    phone_number: str | None = None
    email: str | None = None

# ----- EMPLOYER (CHILD) -----

# Schema for employer /register/
class EmployerCreate(UserCreate):
    company_name: str

class Employer(User):
    company_name: str | None = None

# ----- TOKEN -----

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# ----- TASK -----

class TaskCreate(BaseModel):
    title: str
    description: str

class Task(BaseModel):
    title: str
    description: str
    employer_id: int

# ----- TASK REACTION -----

class TaskReactionCreate(BaseModel):
    title: str
    message: str

class TaskReaction(BaseModel):
    title: str
    message: str
    task_id: int
    developer_id: int

# ----- ACHIEVEMENTS -----

# Base achievement
class Achievement(BaseModel):
    id: int
    title: str
    description: Optional[str]

    class Config:
        orm_mode = True

# Achievement assigned to developer
class DeveloperAchievement(BaseModel):
    id: int
    developer_id: int
    achievement_id: int
    achievement: Achievement
    date_awarded: datetime

    class Config:
        orm_mode = True

# ----- SKILLS -----

# Base skill
class Skill(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# ----- PROFILE -----

# Schema for showing developer profile
class DeveloperProfile(BaseModel):
    username: str
    email: str
    achievements: List[Achievement]

    class Config:
        orm_mode = True