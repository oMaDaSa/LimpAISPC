from core.config import BEDROCK_CONFIG, ANALYSIS_PROMPT_TEMPLATE, BEDROCK_KNOWLEDGE_BASE_ID
import boto3
from services.calculator import Calculator
from services.data_parser import parse_debt_payload
import json

def run_analysis(data: dict):
    try:
        parsed = parse_debt_payload(data)
        
        calc = Calculator()
        metricas_taxas = calc.compute_tax_metrics(
            parsed['rate_type'], 
            parsed['cet_rate'], 
            parsed['market_rate_annual']
        )
        saude_financeira = calc.compute_financial_health(
            parsed['income'], 
            parsed['installment'], 
            parsed['dependents_count']
        )
        impacto_contrato = calc.compute_contract_impact(
            parsed['installment'], 
            parsed['total_loan'], 
            parsed['installments_count']
        )
        analysis_json = {
            "metricas_taxas": metricas_taxas,
            "saude_financeira": saude_financeira,
            "impacto_contrato": impacto_contrato,
            "valor_cesta_basica": parsed['valor_cesta_basica']
        }

        resumo = json.dumps(analysis_json, ensure_ascii=False)
        question = ANALYSIS_PROMPT_TEMPLATE.format(analysis_json=resumo)

        # Usa Bedrock Agent Runtime com Knowledge Base para gerar sem injetar contexto manualmente
        client_kwargs = {"region_name": BEDROCK_CONFIG["region_name"]}
        if "aws_access_key_id" in BEDROCK_CONFIG and "aws_secret_access_key" in BEDROCK_CONFIG:
            client_kwargs["aws_access_key_id"] = BEDROCK_CONFIG["aws_access_key_id"]
            client_kwargs["aws_secret_access_key"] = BEDROCK_CONFIG["aws_secret_access_key"]

        agent_rt = boto3.client("bedrock-agent-runtime", **client_kwargs)

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