import os
import re
import time
import threading
from llama_cpp import Llama
from langdetect import detect, LangDetectException  # New import for language detection
from app.config import settings, get_db_connection  # Import settings

# Load model path from settings
MODEL_PATH = settings.GGUF_MODEL_PATH

# Ensure model exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"GGUF model not found at {MODEL_PATH}")

# Initialize Llama model
llm = Llama(
    model_path=MODEL_PATH,
    n_gpu_layers=0,
    n_threads=8,
    n_ctx=32768,  # Ensure enough context for long documents
    n_batch=512,
    verbose=True
)

def detect_language(text: str) -> str:
    """
    Detect the language of the text using langdetect.
    Fallback to 'en' if detection fails.
    """
    try:
        return detect(text)
    except LangDetectException:
        return "en"

# Function to clean input text
def clean_text(text: str) -> str:
    """
    Remove control characters and normalize whitespace in text.
    Keeping non-ASCII to allow for multilingual summaries.
    """
    # Replace control characters with space
    text = re.sub(r'[\x00-\x09\x0B\x0C\x0E-\x1F\x7F]+', ' ', text)
    # Normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Function to determine summary word limit using a mathematical formula
def calculate_word_limit(text: str) -> int:
    """
    Dynamically adjusts summary length based on input text length using a formula.
    - 1-200 words → 50 words
    - 201-1000 words → 100 words
    - 1001-2000 words → 125 words
    - 2001-4000 words → 150 words
    - 4001+ words → 200 words
    """
    word_count = len(text.split())

    # Apply piecewise function scaling
    summary_words = 50 + 30 * min(8, (word_count - 1) // 1000)
    return summary_words

def generate_summary(text: str) -> str:
    """Generate a concise summary using Llama with dynamic word limits in the detected language."""
    # Clean input text
    text = clean_text(text)
    
    # Detect language
    language = detect_language(text)
    
    # Calculate dynamic word limit
    word_limit = calculate_word_limit(text)
    max_tokens = word_limit * 2  # Adjust token limit
    
    # Construct prompt with language guidance
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that summarizes documents concisely in the same language "
                "as the text. Please ensure your summary is in that language."
            )
        },
        {
            "role": "user",
            "content": (
                f"The text is in '{language}'. Summarize the following document in no more than "
                f"{word_limit} words (in {language}):\n\n{text}"
            )
        }
    ]
    
    try:
        # Generate response
        response = llm.create_chat_completion(messages=messages, max_tokens=max_tokens)
        
        # Extract valid response
        if "choices" in response and response["choices"]:
            summary = response["choices"][0]["message"]["content"].strip()
            return summary
        else:
            return "Error: LLM returned an invalid response."
    except Exception as e:
        return f"Error during LLM execution: {str(e)}"

def queue_worker():
    """Continuously processes pending summarization requests from the database."""
    while True:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the first pending summarization task
        cursor.execute("SELECT * FROM summarization_queue WHERE status = 'pending' ORDER BY id LIMIT 1")
        row = cursor.fetchone()

        if row:
            task_id = row["id"]
            text = row["text"]
            
            # Mark task as processing
            cursor.execute("UPDATE summarization_queue SET status = 'processing' WHERE id = ?", (task_id,))
            conn.commit()

            # Start timer
            start_time = time.time()

            # Generate summary
            summary = generate_summary(text)

            # Calculate processing time
            time_elapsed = time.time() - start_time

            # Update task with results
            cursor.execute(
                "UPDATE summarization_queue SET status = 'completed', result = ?, time_elapsed = ? WHERE id = ?",
                (summary, time_elapsed, task_id)
            )
            conn.commit()

        cursor.close()
        conn.close()
        time.sleep(1)  # Short delay to prevent excessive database queries

# Start worker thread
worker_thread = threading.Thread(target=queue_worker, daemon=True)
worker_thread.start()
