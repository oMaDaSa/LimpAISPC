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
Você é um Assistente de Educação Financeira.
Seu objetivo é ler os dados financeiros abaixo e explicar a situação para o cliente de forma clara e educativa.

**DADOS DO CLIENTE:**
{analysis_json}

---
### GUIA DE ANÁLISE (Use estas regras para compor o texto):

0.  **REGRA DE OURO - VERIFIQUE ANTES DE ESCREVER:**
SE `eh_rotativo` for `false` (Empréstimo Parcelado):
    1. **PROIBIDO:** É estritamente proibido mencionar "teto de 8%", "Resolução 4.765" ou "Cheque Especial" na Seção 1 (Comparativo de Taxas).
    2. **COMPARATIVO:** Compare a taxa do cliente APENAS com a `taxa_mercado`. Se for maior, diga que está acima; se for menor, diga que está abaixo. Ponto final.
    3. **MOTIVO:** Citar o teto do rotativo em contratos parcelados gera confusão jurídica.

SE `eh_rotativo` for `true` (Cheque Especial):
    1. **OBRIGATÓRIO:** Cite a Resolução 4.765 e o teto de 8%.

1.  **Sobre a Taxa (Cheque Especial) - REGRA CRÍTICA:**
    * **ATENÇÃO:** Para Cheque Especial (serie_bcb = '20718'), o Banco Central define um TETO LEGAL de 8% ao mês (Resolução CMN 4.765/2019).
    * **Se taxa ≤ 8% a.m.:** A taxa RESPEITA o limite legal, mesmo que seja maior que a média de mercado (~1.8% a.m.). Diga: "A taxa está DENTRO do teto legal de 8% a.m., porém X% acima da média de mercado."
    * **Se taxa > 8% a.m.:** A taxa VIOLA o limite legal. Diga: "A taxa de X% a.m. ULTRAPASSA o teto legal de 8% estabelecido pela Resolução CMN 4.765/2019."
    * **NÃO CONFUNDA:** Média de mercado (1.8%) ≠ Teto legal (8%). Uma taxa pode estar acima da média e ainda ser LEGAL.

2.  **Sobre a Modalidade:**
    * **Se for Parcelado (`eh_rotativo` = false):** Explique que parcelas fixas trazem previsibilidade. Não cite leis de cartão de crédito.
    * **Se for Rotativo (`eh_rotativo` = true):** 
      - Explique que os juros incidem MENSALMENTE sobre o saldo devedor.
      - Alerte sobre o risco de juros compostos ("bola de neve") se não for quitado integralmente.
      - Mencione que o `pagamento_minimo_mensal` é composto por: juros do mês + 15% de amortização do saldo.

3.  **Verificação de Dados (Sanity Check):**
    * Verifique os campos `custo_total_juros` e `valor_total_a_pagar`.
    * Se forem **menores ou iguais a zero** (negativos): Não tente justificar. Na conclusão, avise: "Os dados de entrada parecem conter inconsistências numéricas".

---
### MODELO DE RESPOSTA (Preencha este modelo mantendo a formatação):

# Análise

## 1. Comparativo de Taxas
(Escreva aqui a comparação da taxa do cliente com a média de mercado).

## 2. Análise da Modalidade
(Escreva aqui a análise sobre ser Rotativo ou Parcelado, baseada no Guia acima).

## 3. Transparência e Custos
(Compare a parcela real com a teórica. Se a real for mais cara, explique sobre o Custo Efetivo Total - CET).

## 4. Saúde Financeira
(Analise o percentual de comprometimento da renda e a sobra frente à cesta básica).

## 5. Resumo e Orientação
* **Valor Original:** R$ ...
* **Total Final:** R$ ...
* **Juros:** R$ ... (Ou aviso de inconsistência se negativo)

**Sugestões Práticas:**
1.  (Sugestão 1)
2.  (Sugestão 2)
3.  (Sugestão 3)

---
**Instrução Final:** Gere a resposta utilizando **exatamente** a estrutura de títulos Markdown acima.
"""