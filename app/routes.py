from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import generate_response, generate_summary
from app.schema import ChatRequest, ChatResponse
from app.database import extract_pdf_text, store_pdf_knowledge, retrieve_relevant_knowledge
from datetime import datetime
from pypdf import PdfReader
import io


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

@router.post("/summarize-pdf/")
async def summarize_pdf(file: UploadFile = File(...)):
    """Upload a PDF, extract its text, and generate a summary."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    try:
        # Read the PDF file
        contents = await file.read()
        pdf_reader = PdfReader(io.BytesIO(contents))

        # Extract text from each page
        text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

        # Generate summary using LLM
        summary = generate_summary(text)

        return {"filename": file.filename, "summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")