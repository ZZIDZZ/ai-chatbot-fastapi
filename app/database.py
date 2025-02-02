import chromadb
from pypdf import PdfReader
import io

# Initialize ChromaDB (stores extracted text from PDFs)
chroma_client = chromadb.PersistentClient(path="db")
collection = chroma_client.get_or_create_collection(name="pdf_knowledge")

def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF file."""
    pdf_reader = PdfReader(io.BytesIO(file_bytes))
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text

def store_pdf_knowledge(text: str, file_name: str):
    """Store extracted PDF knowledge in ChromaDB."""
    collection.add(documents=[text], ids=[file_name])

def retrieve_relevant_knowledge(user_input: str) -> str:
    """Retrieve the most relevant knowledge from ChromaDB."""
    results = collection.query(query_texts=[user_input], n_results=1)
    return results["documents"][0] if results["documents"] else ""
