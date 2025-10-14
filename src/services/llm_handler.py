
import google.generativeai as genai
from typing import List, Dict, Any
import json
from pathlib import Path

from src.core.config import settings
from src.db.models import Message

# --- NEW: Load the Knowledge Base ---
def load_knowledge_base() -> Dict[str, Any]:
    """Loads the FAQ data from the JSON file."""
    kb_path = Path(__file__).resolve().parent.parent.parent / "knowledge_base.json"
    try:
        with open(kb_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"faqs": []}

knowledge_base = load_knowledge_base()
# ------------------------------------


# Configure the Gemini API client
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    # --- THIS IS THE CORRECTED LINE FOR YOUR API KEY ---
    model = genai.GenerativeModel('gemini-2.5-flash') 
    print("Google AI client configured successfully.")
except Exception as e:
    print(f"Error configuring Google AI client: {e}")
    model = None


# --- NEW: Simple Search Function ---
def find_relevant_faq(user_query: str) -> str:
    """
    Finds a relevant FAQ answer from the knowledge base based on keywords.
    Returns the answer string if found, otherwise an empty string.
    """
    user_query = user_query.lower()
    for faq in knowledge_base.get("faqs", []):
        for keyword in faq.get("keywords", []):
            if keyword in user_query:
                return faq.get("answer", "")
    return ""
# -----------------------------------


def generate_bot_response(history: List[Message]) -> str:
    """
    Generates a bot response using RAG and the Google Gemini model.
    """
    if not model:
        return "Error: LLM model is not configured."
        
    user_query = history[-1].content

    # --- NEW: RAG Logic ---
    context_from_kb = find_relevant_faq(user_query)
    # ----------------------

    system_prompt = f"""
    You are a friendly and highly knowledgeable customer support assistant for a company named "InnovateTech".
    Your role is to be helpful, polite, and efficient.
    - If the user seems frustrated or asks for a human, trigger an escalation.
    - Do not make up information. If you don't know the answer, say so.
    
    --- CONTEXT FROM KNOWLEDGE BASE ---
    If the following context is relevant to the user's query, use it to form your answer. Otherwise, ignore it.
    Context: {context_from_kb if context_from_kb else "No specific context found."}
    -----------------------------------
    """

    formatted_history = []
    for msg in history:
        role = "user" if msg.sender == "user" else "model"
        formatted_history.append({"role": role, "parts": [msg.content]})

    full_prompt = [
        {"role": "user", "parts": [system_prompt]},
        {"role": "model", "parts": ["Understood. I am the InnovateTech assistant. How can I help you today?"]},
    ] + formatted_history
    
    try:
        if "human" in user_query.lower() or "agent" in user_query.lower():
             return "I understand you'd like to speak with a human agent. I've escalated your request and someone will be in touch shortly."
        
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        print(f"Error generating response from LLM: {e}")
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again later."
    




def summarize_conversation(history: List[Message]) -> str:
    """
    Uses the LLM to create a concise summary of the conversation.
    """
    if not model:
        return "Error: LLM model is not configured."

    
    transcript = "\n".join(f"{msg.sender.capitalize()}: {msg.content}" for msg in history)

    summary_prompt = f"""
    Please analyze the following customer support conversation and provide a concise, one-paragraph summary.
    The summary should capture the main reason for the customer's inquiry and the final resolution or outcome.

    --- CONVERSATION TRANSCRIPT ---
    {transcript}
    -------------------------------

    Summary:
    """

    try:
        response = model.generate_content(summary_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating summary from LLM: {e}")
        return "Could not generate a summary for this conversation."