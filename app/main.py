from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_and_tables 
from app.routers import  applications, auth, seasons
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(seasons.router)
app.include_router(applications.router)
app.include_router(auth.router)