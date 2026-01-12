import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 

BEDROCK_CONFIG = {
    "region_name": os.getenv("AWS_REGION", "us-east-1"),
    "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
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

BEDROCK_KNOWLEDGE_BASE_ID = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID")

ANALYSIS_PROMPT_TEMPLATE = """
Você é o Consultor Especialista da LimpAI SPC. Seu papel é realizar um diagnóstico 
técnico-jurídico baseado nos dados financeiros do usuário e no seu conhecimento 
especializado (RAG).

DADOS DA ANÁLISE (JSON):
{analysis_json}

CONTEXTO JURÍDICO DISPONÍVEL NO RAG:
1. Lei do Superendividamento (Lei 14.181/2021)
2. Decreto do Mínimo Existencial (Decreto 11.150/2022)
3. Código de Defesa do Consumidor (Artigos 42 e 51)
4. Súmula 530 do STJ

INSTRUÇÕES PARA O LAUDO:

- ABUSIVIDADE DE TAXAS: Se 'tax_abuse_percent' for alto, fundamente com a Súmula 530 do STJ 
(substituição pela taxa média) e o Art. 51 do CDC (cláusulas que colocam o consumidor 
em desvantagem exagerada são nulas).

- MÍNIMO EXISTENCIAL E CESTA BÁSICA: Compare 'family_per_capita_income' com 'valor_cesta_basica'. 
Se houver déficit, use o Decreto 11.150/2022 e a Lei do Superendividamento para explicar 
que a preservação do mínimo existencial é um direito fundamental.

- CONDUTA DE COBRANÇA: Mencione o Art. 42 do CDC para alertar que, mesmo em dívida, o 
consumidor não pode ser exposto ao ridículo ou submetido a qualquer tipo de constrangimento.

- IMPACTO DO CONTRATO: Analise o 'total_interest_cost'. Se o custo for desproporcional ao 
'total_loan_original', utilize a Lei do Superendividamento para falar sobre o 'Crédito Responsável' 
e o dever de informação das instituições financeiras.

FORMATO DE SAÍDA:
- Use Markdown com títulos claros (###).
- Mantenha um tom profissional, acolhedor e focado em soluções.
- Finalize com orientações práticas de renegociação baseadas na Lei 14.181/2021.

Gere o laudo agora:
"""