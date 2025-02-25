import os
import re
import time
import threading
from llama_cpp import Llama
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

# Function to clean input text
def clean_text(text: str) -> str:
    """Remove unwanted characters and normalize whitespace in text."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
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
    summary_words = 50 + 50 * min(4, (word_count - 1) // 800)

    return summary_words

# Function to generate summary using LLM
def generate_summary(text: str) -> str:
    """Generate a concise summary using Llama with dynamic word limits."""
    word_limit = calculate_word_limit(text)  # Calculate dynamic word limit
    max_tokens = word_limit * 2  # Adjust token limit

    text = clean_text(text)  # Clean input text

    # Construct prompt
    messages = [
        {"role": "system", "content": "You are an AI assistant that summarizes documents concisely."},
        {"role": "user", "content": f"Summarize the following document in no more than {word_limit} words:\n\n{text}"}
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

# Worker function for processing queue
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

            # Generate summary with dynamic limits
            summary = generate_summary(text)

            # Calculate processing time
            time_elapsed = time.time() - start_time

            # Update task with results
            cursor.execute(
                "UPDATE summarization_queue SET status = 'completed', result = ?, time_elapsed = ?, input_word_count = ? WHERE id = ?",
                (summary, time_elapsed, len(text.split()), task_id)
            )
            conn.commit()

        cursor.close()
        conn.close()
        time.sleep(1)  # Short delay to prevent excessive database queries

# Start worker thread
worker_thread = threading.Thread(target=queue_worker, daemon=True)
worker_thread.start()
