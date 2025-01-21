from fastapi import FastAPI

from app import database, models
from .routers.developer import router as router_developer
from .routers.employer import router as router_employer

# Create all tables in the database based on the models defined in models.py
# This will ensure that the database schema is set up before the application runs
models.Base.metadata.create_all(bind=database.engine)

# Initialize the FastAPI application
# The FastAPI instance will serve as the main entry point for the API
app = FastAPI()

# Connecting the API routes for developers
# The developer-related endpoints will be accessible under the '/developer' prefix in the API
# This helps in organizing the routes related to developer actions
app.include_router(router_developer, prefix="/developer", tags=["developer"])

# Connecting the API routes for employers
# The employer-related endpoints will be accessible under the '/employer' prefix in the API
# This helps in organizing the routes related to employer actions
app.include_router(router_employer, prefix="/employer", tags=["employer"])
