from core.config import BEDROCK_CONFIG, ANALYSIS_PROMPT_TEMPLATE, BEDROCK_KNOWLEDGE_BASE_ID
import boto3
from services.calculator import Calculator
from services.data_parser import parse_debt_payload
import json

def run_analysis(data: dict):
    try:
        if not BEDROCK_KNOWLEDGE_BASE_ID:
            raise ValueError("BEDROCK_KNOWLEDGE_BASE_ID não configurada. Verifique as variáveis de ambiente.")
        
        parsed = parse_debt_payload(data)
        
        calc = Calculator()
        metricas_taxas = calc.compute_tax_metrics(
            parsed['tipo_taxa'], 
            parsed['taxa_cet'], 
            parsed['taxa_mercado_anual'],
            parsed['serie_bcb']
        )
        saude_financeira = calc.compute_financial_health(
            parsed['renda'], 
            parsed['parcela'], 
            parsed['quantidade_dependentes']
        )
        impacto_contrato = calc.compute_contract_impact(
            parsed['parcela'], 
            parsed['valor_total_emprestimo'], 
            parsed['quantidade_parcelas']
        )
        
        # Análise de custos ocultos (taxas escondidas, seguros, TAC)
        custos_ocultos = calc.compute_hidden_costs(
            total_loan=parsed['valor_total_emprestimo'],
            user_rate_monthly=metricas_taxas['mensal_consumidor'],
            installments_count=parsed['quantidade_parcelas'],
            actual_installment=parsed['parcela'],
            serie_bcb=parsed['serie_bcb']
        )
        
        # Calcular juros acumulados corretamente para rotativo vs parcelado
        if parsed['eh_rotativo']:
            # Para rotativo: juros = quanto a dívida cresceu além do original
            accumulated_interest = parsed['valor_total_fatura'] - parsed['valor_original_divida']
            analyzed_original_debt = parsed['valor_original_divida'] if parsed['valor_original_divida'] > 0 else parsed['valor_total_emprestimo']
        else:
            # Para parcelado: usar cálculo tradicional
            accumulated_interest = impacto_contrato['custo_total_juros']
            analyzed_original_debt = parsed['valor_total_emprestimo']
        
        # cálculo de percentual de juros sobre a dívida
        limite_juros = calc.check_interest_cap(
            original_debt=analyzed_original_debt,
            total_interest_paid=accumulated_interest,
            serie_bcb=parsed['serie_bcb']
        )
        
        analysis_json = {
            "eh_rotativo": parsed['eh_rotativo'],
            "data_contrato": parsed['data_contrato'],
            "serie_bcb": parsed['serie_bcb'],
            "metricas_taxas": metricas_taxas,
            "saude_financeira": saude_financeira,
            "impacto_contrato": impacto_contrato,
            "analise_custos_ocultos": custos_ocultos,
            "limite_juros_rotativos": limite_juros,
            "valor_cesta_basica": parsed['valor_cesta_basica']
        }

        summary = json.dumps(analysis_json, ensure_ascii=False)
        question = ANALYSIS_PROMPT_TEMPLATE.format(analysis_json=summary)

        # Usa Bedrock Agent Runtime com Knowledge Base
        agent_rt = boto3.client(
            "bedrock-agent-runtime",
            region_name=BEDROCK_CONFIG["region_name"]
        )

        response = agent_rt.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": BEDROCK_KNOWLEDGE_BASE_ID,
                    "modelArn": BEDROCK_CONFIG["modelArn"],
                    "generationConfiguration": {
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "temperature": BEDROCK_CONFIG["model_kwargs"]["temperature"],
                                "maxTokens": BEDROCK_CONFIG["model_kwargs"]["max_tokens"],
                                "topP": BEDROCK_CONFIG["model_kwargs"]["top_p"]
                            }
                        }
                    }
                }
            }
        )

        return response["output"]["text"]

    except Exception as e:
        raise Exception(f"Erro na análise completa: {str(e)}")