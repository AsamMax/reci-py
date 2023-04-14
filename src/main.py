import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models.recipies import Base
from .routers import recipies

app = FastAPI()

# Database
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(recipies.router, prefix="/recipies", tags=["recipies"])


# CORS
# TODO: Change to only allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


def dev():
    print("http://127.0.0.1:8000/docs")
    uvicorn.run("src.main:app", port=8000, reload=True)


if __name__ == "__main__":
    dev()
