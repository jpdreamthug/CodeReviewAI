import uvicorn
from fastapi import FastAPI
from app.api import endpoints

app = FastAPI(
    title="Code Review AI",
    description="AI-powered code review tool",
    version="0.1.0"
)

app.include_router(endpoints.router)

def start():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4
    )

def dev():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    dev()
