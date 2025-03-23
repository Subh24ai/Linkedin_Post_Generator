from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os
import streamlit as st

# Load environment variables
load_dotenv()

def get_llm(model_name="llama-3.2-90b-vision-preview", temperature=0.7, max_tokens=1000):
    """
    Get a configured LLM instance with the given parameters.
    Uses API key from environment variables or Streamlit session state.
    """
    # Try to get API key from session state first (for web UI)
    api_key = st.session_state.get("api_key", None) if "st" in globals() else None
    
    # Fall back to environment variable if not in session state
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    
    # Create and return the LLM
    return ChatGroq(
        groq_api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )

# Initialize default LLM
llm = get_llm()

# Function to refresh LLM with new settings
def refresh_llm(model_name=None, temperature=None, max_tokens=None):
    """Refresh the LLM with new settings"""
    global llm
    current_model = getattr(llm, "model_name", "llama-3.2-90b-vision-preview")
    current_temp = getattr(llm, "temperature", 0.7)
    current_max_tokens = getattr(llm, "max_tokens", 1000)
    
    llm = get_llm(
        model_name=model_name or current_model,
        temperature=temperature or current_temp,
        max_tokens=max_tokens or current_max_tokens
    )
    return llm

if __name__ == "__main__":
    response = llm.invoke("What are the two main ingredients in samosa?")
    print(response.content)