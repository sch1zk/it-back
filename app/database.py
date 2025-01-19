# database.py contains database settings and is used for modifying and managing database sessions, as well as connecting to the database itself

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Loading .env and database url from it
load_dotenv()

# If got errors here, check url for mistakes --- postgresql://user:password@localhost/dbname ---
DATABASE_URL = os.getenv("DATABASE_URL")

# Creating connection to database
engine = create_engine(DATABASE_URL)

# Creating session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Not used?
# Base = declarative_base()

# Func to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    