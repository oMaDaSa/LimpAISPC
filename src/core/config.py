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
Você é um Consultor Jurídico Especializado em análise de contratos de crédito e endividamento.

DADOS FINANCEIROS DO CLIENTE:
{analysis_json}

INSTRUÇÕES OBRIGATÓRIAS:

1. Sua resposta DEVE seguir EXATAMENTE este formato Markdown:

# Laudo Técnico-Jurídico de Análise de Crédito

## 1. Abusividade de Taxas de Juros

[Analise as taxas comparando 'mensal_consumidor' com 'mensal_mercado'. Use 'percentual_abuso_taxa'. Cite Súmula 530 do STJ e Art. 51 do CDC se houver abuso.]

## 2. Comprometimento de Renda

[Analise 'comprometimento_renda_pct'. Se > 35%, alerte sobre superendividamento (Lei 14.181/2021).]

## 3. Análise do Mínimo Existencial

[Compare 'renda_per_capita_familiar' com 'valor_cesta_basica'. Use Decreto 11.150/2022.]

## 4. Custos Ocultos e Taxas Embutidas

[Analise 'analise_custos_ocultos'. Se 'valor_taxas_embutidas_mensal' for positivo, explique que há seguros ou TAC não declarados.]

## 5. Impacto Total do Contrato

[Mostre 'valor_total_a_pagar' vs 'valor_total_emprestimo'. Calcule quantas vezes pagará o valor emprestado.]

## 6. Recomendações Jurídicas

[Sugira renegociação com base na Lei 14.181/2021. Oriente sobre direitos do consumidor.]

---

2. Use parágrafos curtos e objetivos.
3. Coloque valores em **negrito**.
4. Use listas quando apropriado.
5. Mantenha tom profissional mas acessível.

GERE O LAUDO AGORA:

**1. ABUSIVIDADE DE TAXAS:**
- Compare 'mensal_consumidor' com 'mensal_mercado'
- Se houver grande diferença, cite a Súmula 530 do STJ e Art. 51 do CDC
- Calcule o percentual de abuso usando 'percentual_abuso_taxa'

**2. COMPROMETIMENTO DE RENDA:**
- Analise 'comprometimento_renda_pct'
- Se maior que 35%, alerte sobre superendividamento (Lei 14.181/2021)

**3. MÍNIMO EXISTENCIAL:**
- Compare 'renda_per_capita_familiar' com 'valor_cesta_basica'
- Use Decreto 11.150/2022 para fundamentar

**4. IMPACTO DO CONTRATO:**
- Mostre 'valor_total_a_pagar' vs 'valor_total_emprestimo'
- Calcule quantas vezes o valor emprestado será pago
- Se desproporcional, cite Crédito Responsável

**5. RECOMENDAÇÕES:**
- Sugira renegociação com base na Lei 14.181/2021
- Oriente sobre direitos do consumidor

FORMATO DE SAÍDA (Markdown):

# Laudo Técnico-Jurídico de Análise de Crédito

## 1. Análise de Taxas de Juros
[conteúdo]

## 2. Comprometimento de Renda
[conteúdo]

## 3. Mínimo Existencial
[conteúdo]

## 4. Impacto Total do Contrato
[conteúdo]

## 5. Recomendações Jurídicas
[conteúdo]

---
**IMPORTANTE:** Use parágrafos separados e títulos claros. Seja objetivo e profissional.

"""