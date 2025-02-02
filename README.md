# AI Chatbot FastAPI

This project is a **Chatbot API Engine** built with **FastAPI**, leveraging a **GGUF format Large Language Model (LLM)**.

## Features

- 🚀 **FastAPI Framework** – High-performance, asynchronous API.
- 🤖 **GGUF Format LLM** – Integrates an advanced Large Language Model.
- 📜 **Auto-generated API Documentation** – Built-in Swagger UI and ReDoc support.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/ZZIDZZ/ai-chatbot-fastapi.git
   cd ai-chatbot-fastapi
   ```

2. **Create and Activate a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:

   Duplicate the `.env.example` file and rename the copy to `.env`.  
   Update the variables in the `.env` file as needed.

5. **Run the Application**:

   ```bash
   uvicorn main:app --reload
   ```

   The API server will be accessible at:

   - 🌍 **Base URL:** `http://localhost:8000`
   - 📄 **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
   - 📘 **ReDoc:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

## Usage

Once the server is running, you can interact with the chatbot API using:

- **Swagger UI (`/docs`)** – An interactive API testing interface.
- **cURL & Postman** – Make API requests manually.
- **FastAPI's Auto-generated Docs (`/redoc`)** – View structured documentation.

## License
This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.