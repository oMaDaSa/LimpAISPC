import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do Bedrock - usa IAM Role em produção, access keys localmente
BEDROCK_CONFIG = {
    "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0", 
    "region_name": os.getenv("AWS_REGION", "us-east-1"),
    "model_kwargs": {
        "temperature": 0.1, 
        "max_tokens": 1000,
        "top_p": 0.9
    }
}

# Adiciona access keys apenas se existirem (para testes locais)
if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
    BEDROCK_CONFIG["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
    BEDROCK_CONFIG["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")

PROMPT_TEMPLATE = """Você é o analista sênior do LimpAI SPC, especialista em legislação financeira e na Lei do Superendividamento.
Responda à pergunta do usuário de forma clara e profissional.

Pergunta: {question}

Resposta:"""