from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import uvicorn

from app.api import notes, templates, users
import app.models as models
from app.database import engine

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(notes.router)
app.include_router(templates.router)
app.include_router(users.router)

app.mount("/", StaticFiles(directory="/"), name="main")


@app.get("/")
async def hello():
    return "Hello!"

