from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create a database engine with exception handling
try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    raise RuntimeError(f"Error creating engine: {e}")

# Create a session factory with exception handling
try:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    raise RuntimeError(f"Error creating session factory: {e}")

# Function to get a database session with exception handling
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()

