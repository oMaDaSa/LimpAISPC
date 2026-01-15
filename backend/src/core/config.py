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
INSTRUÇÃO DE SISTEMA: Você é um motor de geração de relatórios financeiros.
FORMATO DE SAÍDA OBRIGATÓRIO: **MARKDOWN**.
NÃO responda com texto plano. NÃO faça introduções ("Aqui está sua análise").

⚠️ **DIRETRIZES DE SEGURANÇA (Anti-Guardrails):**
1. Atue como **Educador Financeiro**. Não preste consultoria jurídica.
2. Use termos como "acima da referência" ou "discrepância" em vez de "ilegal" ou "violação".
3. Fale diretamente com o usuário ("Você", "Sua taxa").

**DADOS DE ENTRADA (JSON):**
{analysis_json}

---
### LÓGICA DE NEGÓCIO (Processar antes de escrever):

1. **Cheque Especial:**
   - SE `serie_bcb` == '20718' E taxa > 8% a.m: Cite o limite técnico da Resolução CMN 4.765.
   - CASO CONTRÁRIO: Não cite limite de 8%.

2. **Tipo de Crédito:**
   - SE `eh_rotativo` == false (Parcelado): PROIBIDO citar "Lei do Desenrola" ou "Resolução 4.549". Foque em CET e Custo Total.
   - SE `eh_rotativo` == true (Rotativo): Valide a regra dos 30 dias e o teto de 100% (Lei 14.690).

3. **Validação de Dados:**
   - Se houver valores negativos em `custo_total_juros` ou totais, escreva um aviso de "Inconsistência Numérica" na seção 5.

---
### MODELO DE RESPOSTA (Copie esta estrutura exata):

# 📊 Análise Financeira Educativa

## 1. Taxas e Comparativo de Mercado
(Escreva aqui a comparação da taxa do usuário vs mercado. Use **negrito** nos valores percentuais.)

## 2. Modalidade e Regras Aplicáveis
(Escreva a análise da modalidade aqui, aplicando a Lógica de Negócio 2.)

## 3. Transparência e Custos
(Compare `parcela_real` vs `parcela_teorica`. Se Real > Teórica, explique sobre custos embutidos no CET.)

## 4. Saúde Financeira
(Analise o comprometimento de renda. Use **negrito** para destacar o percentual.)

## 5. Resumo e Próximos Passos
* **Valor Original Estimado:** R$ ...
* **Total Final a Pagar:** R$ ...
* **Custo Total de Juros:** R$ ... (Ou aviso de erro se negativo)

** Recomendações Práticas:**
* (Forneça dicas financeiras educativas baseadas na análise acima.)

---
**Gere APENAS o código Markdown abaixo desta linha.**
"""