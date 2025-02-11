import os
from llama_cpp import Llama
from app.config import settings, get_db_connection  # Import settings
import re
import time
import threading
import sqlite3
from uuid import uuid4

# Get model path from settings
MODEL_PATH = settings.GGUF_MODEL_PATH
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"GGUF model not found at {MODEL_PATH}")

# llm = Llama(
#     model_path=MODEL_PATH,
#     n_gpu_layers=0,
#     n_threads=8,
#     n_ctx=8192,
#     n_batch=512,
#     verbose=True
# )

llm = Llama(
    model_path=MODEL_PATH,
    n_gpu_layers=0,
    n_threads=8,
    n_ctx=8192,
    n_batch=512,
    verbose=True
)

def clean_text(text: str) -> str:
    """Remove unwanted characters and normalize whitespace in text."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
    return text

# Summarization function (simulated with sleep)
def generate_summary(text: str) -> str:
    """Generate a clean and concise summary using Llama."""
    word_limit = 100  # Limit words in summary
    max_tokens = int(word_limit * 2)  # Adjust tokens

    text = clean_text(text)  # Clean input text

    prompt = f"""
    Summarize the following academic paper in clear, concise language with no more than {word_limit} words.

    Document:
    {text}

    Summary:
    """

    response = llm(prompt, max_tokens=max_tokens)
    print("Raw Llama Output:", response)

    
    if "choices" not in response:
        return "Error: Invalid model output"

    summary = response["choices"][0]["text"].strip()

    # Trim summary if it's too long
    words = summary.split()
    if len(words) > word_limit:
        summary = " ".join(words[:word_limit]) + "..."

   # simulate 10 second process using sleep
    # summary = "the summary of this document is I don't give a flick"
    # time.sleep(5)

    return summary

# Queue worker function
def queue_worker():
    while True:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM summarization_queue WHERE status = 'pending' ORDER BY id LIMIT 1")
        row = cursor.fetchone()

        if row:
            task_id = row["id"]
            text = row["text"]
            cursor.execute("UPDATE summarization_queue SET status = 'processing' WHERE id = ?", (task_id,))
            conn.commit()

            summary = generate_summary(text)
            cursor.execute("UPDATE summarization_queue SET status = 'completed', result = ? WHERE id = ?", (summary, task_id))
            conn.commit()

        cursor.close()
        conn.close()
        time.sleep(1)  # Small delay to avoid excessive database queries

# Start worker thread
worker_thread = threading.Thread(target=queue_worker, daemon=True)
worker_thread.start()


