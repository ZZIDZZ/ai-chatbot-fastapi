from pydantic import BaseModel
from datetime import datetime

# Request Schema
class ChatRequest(BaseModel):
    input: str

# Response Schema
class ChatResponse(BaseModel):
    status: str
    time: str
    input: str
    output: str

def format_response(user_input: str, ai_output: str) -> ChatResponse:
    """Format response in JSON structure."""
    return ChatResponse(
        status="success",
        time=datetime.utcnow().isoformat() + "Z",
        input=user_input,
        output=ai_output
    )
