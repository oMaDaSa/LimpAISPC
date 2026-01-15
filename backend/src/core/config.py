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
        "temperature": 0.2, 
        "max_tokens": 4096,
        "top_p": 0.7
    }
}

# Adiciona access keys apenas se existirem (para testes locais)
if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
    BEDROCK_CONFIG["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
    BEDROCK_CONFIG["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")

BEDROCK_KNOWLEDGE_BASE_ID = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID")

API_PASSWORD = os.getenv("PASSWORD", "123456789")

ANALYSIS_PROMPT_TEMPLATE = """
INSTRUÇÃO DE SISTEMA: Você é um Assistente de Educação Financeira (IA).
OBJETIVO: Explicar os dados para o cliente de forma direta ("Você", "Sua taxa").
FORMATO DE SAÍDA: **MARKDOWN RIGOROSO** (Não use texto plano).

**DADOS DO CLIENTE:**
{analysis_json}

---
### REGRAS DE LÓGICA (Processamento Interno):

1. **Sobre Cheque Especial (Código 20718):**
   - Apenas se `serie_bcb` for '20718' E a taxa for > 8% a.m.: Cite que o valor ultrapassa o parâmetro da Resolução CMN 4.765.
   - Caso contrário: Não cite o teto de 8%.

2. **Sobre Leis e Modalidade:**
   - Se `eh_rotativo` for **FALSE**: Não cite "Lei do Desenrola" ou "Resolução 4.549". Foque em previsibilidade e CET.
   - Se `eh_rotativo` for **TRUE**: Explique o risco da "bola de neve" e verifique os parâmetros da Lei 14.690 (teto de 100%).

3. **Verificação de Sanidade:**
   - Se houver valores negativos em juros ou totais: Avise na Seção 5 sobre "Inconsistência nos dados de entrada".

---
### ESTRUTURA DA RESPOSTA (Preencha este modelo em Markdown):

# 📊 Análise Financeira Educativa

## 1. Taxas e Comparativo de Mercado
(Compare a taxa do cliente com a do mercado. Seja direto: "Sua taxa é X%...")

## 2. Modalidade e Regras
(Aplique a REGRA DE LÓGICA 2 aqui. Identifique se é Rotativo ou Parcelado e explique os riscos.)

## 3. Transparência e Custos
(Compare `parcela_real` vs `parcela_teorica`. Se a Real for maior, explique sobre custos ocultos no CET.)

## 4. Saúde Financeira
(Analise o comprometimento de renda e a sobra frente à cesta básica.)

## 5. Resumo e Próximos Passos
* **Valor Original:** R$ ...
* **Total a Pagar:** R$ ...
* **Custo de Juros:** R$ ... (Ou aviso de inconsistência se for negativo)

**3 Ações Práticas:**
1. (Ação 1)
2. (Ação 2)
3. (Ação 3)

---
**Gere APENAS o conteúdo Markdown acima, sem introduções.**
"""