#!/bin/bash

# Define the virtual environment path
VENV_PATH="/home/pttas/ai-chatbot-fastapi/ai_env/bin/activate"

# Check if the virtual environment exists
if [ ! -f "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Activate the virtual environment
source "$VENV_PATH"

# Run Uvicorn with the specified command
#uvicorn app.main:app --reload --host 0.0.0.0
gunicorn -k uvicorn.workers.UvicornWorker app.main:app -b '0.0.0.0:8000'