from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRoute
from app.config import settings  # Import settings
from app.routes import router

# Initialize FastAPI
app = FastAPI(
    title="BIMO Chatbot API", 
    version="1.1",
)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
