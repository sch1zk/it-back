# schemas.py is used to describe schemas that will be used to validate input and output data when interacting with an API
# It helps transform data between query representations and database models, and is also used to validate data coming from the client

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    username: str
    email: str

    class Config:
        # old orm_mode = True, to return objects not dicts
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
