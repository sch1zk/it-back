# schemas.py is used to describe schemas that will be used to validate input and output data when interacting with an API
# It helps transform data between query representations and database models, and is also used to validate data coming from the client

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    username: str
    email: str | None = None
    # sch1zk: Maybe it'll be useful soon
    # full_name: str | None = None

    # sch1zk: Do we really need this for now? Commented because of official docs
    # class Config:
    #     # old orm_mode = True, to return objects not dicts
    #     from_attributes = True

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
