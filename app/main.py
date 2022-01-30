from fastapi import FastAPI

from .internal import admin
from .routers import files, users, auth
from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)

description = """
Simple Blob Storage System. 🚀

## Admin

Opeartions only admin can perform with users and files.

## Authentication

* **Get token**
* **Create session**
* **View if session exists**
* **Logout and delete session**
"""

app = FastAPI(
    title="Simple Blob Storage System",
    description=description,
    contact={
        "name": "Daniel Davdraj",
        "email": "danieldavidraj23@gmail.com",
    },
    docs_url="/swagger", 
    redoc_url=None
)

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(files.router)

@app.get("/")
async def root():
    return {"message": "Blob storage system"}
