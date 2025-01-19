from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app import auth, crud, database, models, schemas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

@app.post("/register/", response_model=schemas.Developer)
def register_dev(user: schemas.DeveloperCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_dev_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    return crud.create_dev(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_dev_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(database.get_db)
    ) -> schemas.Token:
    user = auth.authenticate_dev(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": form_data.username}
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

@app.post("/employer/register/", response_model=schemas.Employer)
def register_emp(user: schemas.EmployerCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_emp_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    return crud.create_emp(db=db, user=user)

@app.post("/employer/token", response_model=schemas.Token)
def login_emp_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(database.get_db)
    ) -> schemas.Token:
    user = auth.authenticate_emp(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": form_data.username}
    )
    return schemas.Token(access_token=access_token, token_type="bearer")