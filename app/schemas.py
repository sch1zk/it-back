from datetime import date
from pydantic import BaseModel


# ----- USER (PARENT) -----

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    username: str
    email: str | None = None
    # sch1zk: Do we really need this for now? Commented because of official docs
    # class Config:
    #     # old orm_mode = True, to return objects not dicts
    #     from_attributes = True

class UserInDB(User):
    hashed_password: str


# ----- DEVELOPER (CHILD) -----

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


# ----- EMPLOYER (CHILD) -----

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