from langchain_google_genai import ChatGoogleGenerativeAI

from core.config import LLM_CONFIG

def ai_response(user_input: str):
    llm = ChatGoogleGenerativeAI(**LLM_CONFIG)
    
    response = llm.invoke(user_input)
    
    return response.content