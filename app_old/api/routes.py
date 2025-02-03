from fastapi import FastAPI

from app import database, models
from .routers.developer import router as router_developer
from .routers.employer import router as router_employer

# Create all tables in the database
models.Base.metadata.create_all(bind=database.engine)

# Initialize the FastAPI application
app = FastAPI()

# Include developer routes
app.include_router(router_developer, prefix="/developer", tags=["developer"])

# Include employer routes
app.include_router(router_employer, prefix="/employer", tags=["employer"])
