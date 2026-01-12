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
Você é um consultor jurídico especializado em contratos de crédito e defesa do consumidor no Brasil.

Analise os dados financeiros abaixo e elabore um laudo técnico-jurídico completo em Markdown:

{analysis_json}

Estruture sua análise usando os dados do JSON com os seguintes tópicos:

# Laudo Técnico-Jurídico de Análise de Crédito

## 1. Análise de Taxas de Juros
Compare 'mensal_consumidor' com 'mensal_mercado' (ambos em metricas_taxas). 
Mostre o 'percentual_abuso_taxa'. Se houver diferença significativa, explique usando a Súmula 530 do STJ e Art. 51 do CDC.

## 2. Comprometimento de Renda
Use 'comprometimento_renda_pct' (em saude_financeira). 
Se superior a 35%, mencione a Lei do Superendividamento (14.181/2021).

## 3. Mínimo Existencial
Compare 'renda_per_capita_familiar' (em saude_financeira) com 'valor_cesta_basica'. 
Fundamente com o Decreto 11.150/2022.

## 4. Custos Ocultos
Use os dados de 'analise_custos_ocultos':
- Compare 'parcela_teorica' com 'parcela_real'
- Se 'valor_taxas_embutidas_mensal' for positivo, explique que há seguros ou TAC não declarados
- Mostre 'impacto_total_taxas_embutidas'

## 5. Impacto Total do Contrato
Use 'impacto_contrato':
- Mostre 'valor_total_a_pagar' vs 'valor_total_emprestimo'
- Destaque 'custo_total_juros'
- Calcule quantas vezes o cliente pagará o valor emprestado

## 6. Recomendações
Sugira ações práticas de renegociação baseadas na Lei 14.181/2021 e oriente sobre direitos do consumidor.

Use linguagem clara, valores em **negrito**, e mantenha tom profissional e acolhedor.
"""