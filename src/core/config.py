from dotenv import load_dotenv

load_dotenv()

BEDROCK_CONFIG = {
    "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0", 
    "region_name": "us-east-1",
    "model_kwargs": {
        "temperature": 0.1, 
        "max_tokens": 1000,
        "top_p": 0.9
    }
}

PROMPT_TEMPLATE = """Você é o analista sênior do LimpAI SPC, especialista em legislação financeira e na Lei do Superendividamento.
Responda à pergunta do usuário de forma clara e profissional.

Pergunta: {question}

Resposta:"""