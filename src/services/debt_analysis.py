from langchain_aws import ChatBedrock
from core.config import BEDROCK_CONFIG, ANALYSIS_PROMPT_TEMPLATE
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

        llm = ChatBedrock(
            model_id=BEDROCK_CONFIG["model_id"],
            region_name=BEDROCK_CONFIG["region_name"],
            model_kwargs=BEDROCK_CONFIG.get("model_kwargs", {})
        )
        response = llm.invoke(question)
        return response.content

    except Exception as e:
        raise Exception(f"Erro na análise completa: {str(e)}")