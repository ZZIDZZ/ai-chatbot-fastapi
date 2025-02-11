from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import generate_summary, clean_text, generate_summary, queue_worker 
from app.schema import ChatRequest, ChatResponse
from app.database import extract_pdf_text, store_pdf_knowledge, retrieve_relevant_knowledge
from datetime import datetime
from pypdf import PdfReader
import io
from app.config import settings, get_db_connection
from uuid import uuid4


router = APIRouter()

# @router.post("/chat", response_model=ChatResponse)
# def chatbot(request: ChatRequest):
#     """Handle chatbot requests with optional PDF knowledge retrieval."""
#     knowledge = retrieve_relevant_knowledge(request.input)
#     ai_output = generate_response(request.input, knowledge)
    
#     return ChatResponse(
#         status="success",
#         time=datetime.utcnow().isoformat() + "Z",
#         input=request.input,
#         output=ai_output
#     )

# @router.post("/upload-pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     """Upload a PDF, extract its text, and store it as knowledge."""
#     if file.content_type != "application/pdf":
#         raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
#     contents = await file.read()
#     text = extract_pdf_text(contents)
#     store_pdf_knowledge(text, file.filename)
    
#     return {"message": "File uploaded successfully", "filename": file.filename}

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

@router.post("/summarize")
def submit_summarization(text: str):
    task_id = str(uuid4())
    text = clean_text(text)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO summarization_queue (id, text) VALUES (?, ?)", (task_id, text))
    conn.commit()
    cursor.close()
    conn.close()
    
    return {"task_id": task_id, "status": "queued"}

@router.get("/summary/{task_id}")
def get_summary(task_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, result FROM summarization_queue WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return {"error": "Task not found"}
    return {"task_id": task_id, "status": row["status"], "result": row["result"]}