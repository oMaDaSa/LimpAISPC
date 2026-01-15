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
ATUE COMO: Assistente de Inteligência Artificial focado em **Educação Financeira**.
OBJETIVO: Explicar didaticamente os dados, sem prestar consultoria jurídica oficial.

⚠️ **DIRETRIZES DE SEGURANÇA (Para evitar bloqueio):**
1. **Não acuse crimes:** Nunca use termos como "fraude", "crime", "violação legal" ou "ilegal".
2. **Use termos técnicos:** Em vez de "violação", use "está acima do limite regulatório" ou "divergência".
3. **Persona:** Você é um educador, não um advogado. Fale DIRETAMENTE com o usuário ("Você", "Sua taxa").

**DADOS DO CLIENTE:**
{analysis_json}

---
### REGRAS DE LÓGICA (Siga Estritamente):

1. **Cheque Especial (Código 20718):**
   - **SE** `serie_bcb` for '20718' E a taxa mensal for > 8%: Informe que a taxa ultrapassa o limite técnico da Resolução CMN 4.765.
   - **SE** for qualquer outra modalidade: NÃO cite teto de 8%.

2. **Contexto de Crédito (Rotativo vs Parcelado):**
   - **SE `eh_rotativo` for `false` (Parcelado):** Você está PROIBIDO de citar "Resolução CMN 4.549" ou "Lei do Desenrola". Foque apenas no CET e previsibilidade.
   - **SE `eh_rotativo` for `true` (Rotativo):** Explique o conceito de "bola de neve" e valide se o teto de 100% (Lei 14.690) está sendo observado (para contratos pós-2024).

3. **Verificação de Sanidade (Dados Inconsistentes):**
   - Se encontrar valores negativos ou zerados em campos de juros/totais: Avise na Seção 5 que "Os dados inseridos parecem conter inconsistências numéricas" e peça revisão.

---
### ESTRUTURA OBRIGATÓRIA (Markdown Rigoroso):

# 📊 Análise Financeira Educativa

## 1. Taxas e Comparativo
(Compare `mensal_consumidor` vs `mensal_mercado`. Diga: "Sua taxa é X%, enquanto a média é Y%". Aplique a REGRA 1 aqui.)

## 2. Modalidade e Regras
(Identifique se é Rotativo ou Parcelado. Aplique a REGRA 2 aqui. Explique os riscos técnicos da modalidade.)

## 3. Transparência e Custos
(Compare `parcela_real` vs `parcela_teorica`. Se a Real for maior, explique didaticamente que isso indica custos adicionais no CET, como seguros ou tarifas.)

## 4. Saúde Financeira
(Analise `comprometimento_renda_pct`. Se > 30%, alerte sobre o risco orçamentário. Compare renda familiar com `valor_cesta_basica`.)

## 5. Resumo e Próximos Passos
- **Resumo dos Valores:**
  - Valor Original da Dívida: R$ ...
  - Total Estimado a Pagar: R$ ...
  - Custo de Juros: R$ ... (Se negativo, avise sobre erro de digitação)
- **Orientações Práticas:** (Ex: Portabilidade, Renegociação, Solicitação de planilha DED).

---
**IMPORTANTE:** Gere apenas o relatório formatado em Markdown. Não faça preâmbulos.
"""