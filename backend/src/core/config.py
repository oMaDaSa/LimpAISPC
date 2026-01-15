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
ATUE COMO: Consultor Financeiro Especialista.
FORMATO DE SAÍDA: **MARKDOWN RIGOROSO**.

Sua tarefa é analisar os dados abaixo e gerar um relatório estruturado para o cliente.
Fale DIRETAMENTE com ele ("Você", "Sua taxa"). Não use "O usuário".

**DADOS DO CLIENTE:**
{analysis_json}

---
### REGRAS DE LÓGICA (Siga Estritamente):

1. **Cheque Especial (Código 20718):**
   - APENAS se `serie_bcb` for '20718' E a taxa mensal for > 8%: Critique e cite a Resolução CMN 4.765.
   - Se for qualquer outra modalidade: NÃO cite teto de 8%.

2. **Leis de Rotativo (Lei Desenrola / CMN 4.549):**
   - APENAS se `eh_rotativo` for `true`: Valide essas leis.
   - Se `eh_rotativo` for `false`: NÃO cite essas leis. Foque em CET e Custo Total.

3. **Valores Negativos/Inconsistentes:**
   - Se encontrar valores negativos em juros ou totais: Avise sobre "Inconsistência de Dados" na Seção 5 e não tente justificar o injustificável.

---
### ESTRUTURA OBRIGATÓRIA DA RESPOSTA (Use exatamente estes títulos):

# 📊 Análise Financeira Educativa

## 1. Taxas e Comparativo de Mercado
(Compare a taxa `mensal_consumidor` com `mensal_mercado`. Seja direto: "Sua taxa é X, a média é Y".)

## 2. Modalidade e Regras
(Identifique se é Rotativo ou Parcelado. Aplique a REGRA DE LÓGICA 2 aqui. Explique os riscos específicos da modalidade detectada.)

## 3. Transparência e Custos Ocultos
(Compare `parcela_real` vs `parcela_teorica`. Se Real > Teórica, explique que há taxas embutidas inflando o CET.)

## 4. Saúde Financeira
(Analise `comprometimento_renda_pct` e a sobra frente à `valor_cesta_basica`. Alerte se o orçamento estiver em risco.)

## 5. Resumo e Plano de Ação
- **Resumo Financeiro:**
  - Valor Original: R$ ...
  - Total a Pagar: R$ ...
  - Juros Totais: R$ ... (Se for negativo, diga "Erro nos dados de entrada")
- **3 Ações Práticas:** (Dê 3 passos concretos para o cliente sair dessa dívida).

---
**IMPORTANTE:** Não escreva frases introdutórias como "Aqui está sua análise". Comece diretamente pelo título "# 📊 Análise Financeira Educativa". Use negrito (**texto**) para destacar números.
"""