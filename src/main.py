import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


def dev():
    uvicorn.run("src.main:app", port=8000, reload=True)
