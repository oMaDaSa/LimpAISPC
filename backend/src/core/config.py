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
ROLE: Você é um Assistente de Análise de Dados.
TAREFA: Transformar os dados financeiros brutos do JSON em um relatório informativo e legível.
FORMATO DE SAÍDA: Markdown.

⚠️ **DIRETRIZES DE CONTEÚDO (Para evitar bloqueios):**
1. **Natureza:** Sua resposta é estritamente **INFORMATIVA**. Não dê conselhos legais ou de investimento.
2. **Vocabulário:** Evite "violação", "ilegal", "crime". Use "acima da referência", "divergência", "ponto de atenção".
3. **Foco:** Analise os números. Não julgue a moralidade do contrato.

**DADOS JSON:**
{analysis_json}

---
### REGRAS DE EXIBIÇÃO:

1. **Sobre Taxas (Cheque Especial):**
   - SE `serie_bcb` for '20718' E taxa > 8%: Mencione que o valor está acima do parâmetro da Resolução CMN 4.765.
   - OUTROS CASOS: Apenas compare com a média de mercado.

2. **Sobre Modalidade:**
   - SE `eh_rotativo` for `false`: Não mencione regras de rotativo (Lei do Desenrola/30 dias). Foque apenas no custo da parcela.
   - SE `eh_rotativo` for `true`: Explique que esta modalidade tem custos progressivos e cite as diretrizes de teto de juros para contratos recentes.

3. **Inconsistências:**
   - Se o JSON tiver valores negativos em Juros ou Totais, escreva na seção 5: "Nota: Os dados de entrada parecem conter inconsistências numéricas (valores negativos) que impedem um cálculo exato."

---
### ESTRUTURA DA RESPOSTA (Gere APENAS o conteúdo abaixo):

# 📊 Relatório de Dados Financeiros

## 1. Comparativo de Taxas
(Texto comparando a taxa do cliente com a média de mercado. Seja objetivo.)

## 2. Análise da Modalidade
(Identifique a modalidade. Se for Rotativo, explique os riscos de acumulação. Se for Parcelado, explique a vantagem da parcela fixa.)

## 3. Composição de Custos
(Compare `parcela_real` com `parcela_teorica`. Se a Real for maior, explique didaticamente que a diferença compõe o Custo Efetivo Total - CET.)

## 4. Indicadores de Orçamento
(Analise o percentual de comprometimento da renda. Se alto, sugira atenção.)

## 5. Resumo dos Dados
* **Valor Original:** R$ ...
* **Total Estimado:** R$ ...
* **Juros Calculados:** R$ ... (Ou aviso de inconsistência se negativo)

**Sugestões Práticas:**
1. (Sugestão genérica 1)
2. (Sugestão genérica 2)
3. (Sugestão genérica 3)

---
"""