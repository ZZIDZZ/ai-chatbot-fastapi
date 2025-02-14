from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from app.models import generate_summary, clean_text, queue_worker
from app.schema import ChatRequest, ChatResponse
from app.database import extract_pdf_text, store_pdf_knowledge, retrieve_relevant_knowledge
from datetime import datetime
from pypdf import PdfReader
import io
from app.config import settings, get_db_connection
from uuid import uuid4

def verify_password(password: str = Query(...)):
    """Middleware to verify password before processing any request."""
    if password != settings.PROMPT_PASSWORD:
        raise HTTPException(status_code=403, detail="Forbidden: Incorrect password")
    return password

router = APIRouter()

@router.post("/summarize-pdf/")
async def summarize_pdf(file: UploadFile = File(...), password: str = Depends(verify_password)):
    """Upload a PDF, extract its text, and generate a summary."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    try:
        contents = await file.read()
        pdf_reader = PdfReader(io.BytesIO(contents))
        text = clean_text("\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()]))
        task_id = str(uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO summarization_queue (id, text) VALUES (?, ?)", (task_id, text))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"filename": file.filename, "task_id": task_id, "status": "queued"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")

@router.post("/summarize")
def submit_summarization(text: str, password: str = Depends(verify_password)):
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
def get_summary(task_id: str, password: str = Depends(verify_password)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, result FROM summarization_queue WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task_id": task_id, "status": row["status"], "result": row["result"]}
