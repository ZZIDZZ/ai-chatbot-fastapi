from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import generate_response
from app.schema import ChatRequest, ChatResponse
from app.database import extract_pdf_text, store_pdf_knowledge, retrieve_relevant_knowledge
from datetime import datetime

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chatbot(request: ChatRequest):
    """Handle chatbot requests with optional PDF knowledge retrieval."""
    knowledge = retrieve_relevant_knowledge(request.input)
    ai_output = generate_response(request.input, knowledge)
    
    return ChatResponse(
        status="success",
        time=datetime.utcnow().isoformat() + "Z",
        input=request.input,
        output=ai_output
    )

@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF, extract its text, and store it as knowledge."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    contents = await file.read()
    text = extract_pdf_text(contents)
    store_pdf_knowledge(text, file.filename)
    
    return {"message": "File uploaded successfully", "filename": file.filename}
