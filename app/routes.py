from fastapi import APIRouter
from app.models import generate_response
from app.schema import ChatRequest, format_response

# Initialize Router
router = APIRouter()

@router.post("/chat")
def chatbot(request: ChatRequest):
    """Handle chatbot request"""
    ai_output = generate_response(request.input)
    return format_response(request.input, ai_output)
