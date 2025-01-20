from fastapi import FastAPI

from app import database, models
from .routers.developer import router as router_developer
from .routers.employer import router as router_employer

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Connecting API for developers
app.include_router(router_developer, prefix="/developer", tags=["developer"])

# Connecting API for employers
app.include_router(router_employer, prefix="/employer", tags=["employer"])