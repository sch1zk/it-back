from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Loading .env file and reading environment variables
load_dotenv()  # This loads the environment variables from a `.env` file to make them available in the program

# Fetching the database URL from environment variables
# The format for the URL is: postgresql://user:password@localhost/dbname
DATABASE_URL = os.getenv("DATABASE_URL")  # Reads the DATABASE_URL variable from the .env file

# Creating a connection to the database using the provided DATABASE_URL
# This engine is responsible for connecting to the database and executing queries
engine = create_engine(DATABASE_URL)  # `create_engine` creates a connection pool to interact with the database

# Creating a session factory to handle sessions with the database
# Sessions manage the transactions and interactions with the database during a request/operation
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  
# - autocommit=False: prevents automatic commit of transactions (must commit manually)
# - autoflush=False: prevents automatic flushing of session (flush only when needed)
# - bind=engine: associates the session with the previously created engine

# Base = declarative_base()  
# This line is commented out and not in use, but it would typically be used to define the base class for declarative ORM models.

# Function to get a database session
def get_db():
    db = SessionLocal()  # Creates a new session instance using the session factory
    try:
        yield db  # Yield the database session, allowing the caller to use it
    finally:
        db.close()  # Ensure that the session is properly closed when the database operation is done

    