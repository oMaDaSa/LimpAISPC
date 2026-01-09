'''
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import os

load_dotenv()

LLM_CONFIG = {
    "model": "gemini-2.0-flash",
    "temperature": 0,
    "google_api_key": os.getenv("GOOGLE_API_KEY")
}

SUPABASE_CONFIG = {
    "url": os.getenv("SUPABASE_URL"),
    "key": os.getenv("SUPABASE_KEY"),
}

#########################
template_string = """Você é o analista sênior do LimpAI SPC, especialista em legislação financeira e na Lei do Superendividamento.
Use os seguintes pedaços de contexto recuperado para responder à pergunta do usuário. 
Se você não souber a resposta com base no contexto, diga que não tem informações específicas, mas forneça uma orientação geral baseada em boas práticas financeiras.

CONTEXTO RELEVANTE:
{context}

PERGUNTA DO USUÁRIO:
{question}

RESPOSTA DO ESPECIALISTA (cite artigos da lei se disponíveis):"""

# Criando o objeto PromptTemplate
PROMPT_TEMPLATE = PromptTemplate(
    template=template_string,
    input_variables=["context", "question"]
)
'''