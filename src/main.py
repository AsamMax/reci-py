import uvicorn
from fastapi import FastAPI

from .database import engine
from .models.recipies import Base
from .routers import recipies

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(recipies.router, prefix="/recipies", tags=["recipies"])


@app.get("/")
async def root():
    return {"message": "Hello World"}


def dev():
    print("http://127.0.0.1:8000/docs")
    uvicorn.run("src.main:app", port=8000, reload=True)
