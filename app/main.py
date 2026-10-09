from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables 
from app.routers import  seasons

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app.include_router(seasons.router)