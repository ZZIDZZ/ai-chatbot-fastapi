from fastapi import FastAPI
from app.routes import router

# Initialize FastAPI
app = FastAPI(title="GGUF Chatbot API", version="1.0")

# Include routes from app
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
