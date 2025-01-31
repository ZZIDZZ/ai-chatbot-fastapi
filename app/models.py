from llama_cpp import Llama

# Load GGUF Model
MODEL_PATH = "merged_model.gguf"  # Change this to your model path
llm = Llama(model_path=MODEL_PATH, n_ctx=2048)

def generate_response(user_input: str) -> str:
    """Generate AI response from GGUF model."""
    response = llm(user_input, max_tokens=256)
    return response["choices"][0]["text"].strip()
