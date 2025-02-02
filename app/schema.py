from pydantic import BaseModel
from datetime import datetime
import re

# Request Schema
class ChatRequest(BaseModel):
    input: str

# Response Schema
class ChatResponse(BaseModel):
    status: str
    time: str
    input: str
    output_raw: str
    output_formatted: str
    output_think: str

def format_response(user_input: str, ai_output: str) -> ChatResponse:
    """Format response into structured JSON."""
    
    # Split the response at '</think>'
    parts = ai_output.split('</think>', 1)
    
    # Extract 'thought' and 'output' based on the split
    output_think = parts[0].replace('<think>', '').strip() if len(parts) > 1 else ""
    output_formatted = parts[1].strip() if len(parts) > 1 else parts[0].strip()

    return ChatResponse(
        status="success",
        time=datetime.utcnow().isoformat() + "Z",
        input=user_input,
        output_raw=ai_output,
        output_formatted=output_formatted,
        output_think=output_think
    )

