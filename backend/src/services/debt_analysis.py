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
        tax_metrics = calc.compute_tax_metrics(
            parsed['tipo_taxa'], 
            parsed['taxa_cet'], 
            parsed['taxa_mercado_anual'],
            parsed['serie_bcb']
        )

        if parsed['eh_rotativo']:
            current_outstanding_balance = parsed['valor_total_fatura']
            monthly_rate_decimal = tax_metrics['mensal_consumidor'] / 100
            
            # Juros mensais projetados: saldo × taxa
            projected_monthly_interest = current_outstanding_balance * monthly_rate_decimal
            
            # Amortização mínima: 15% do saldo (padrão bancário)
            minimum_amortization_percentage = 0.15
            minimum_amortization = current_outstanding_balance * minimum_amortization_percentage
            
            # Pagamento mínimo mensal = juros + amortização
            effective_installment = projected_monthly_interest + minimum_amortization
            
            # Variáveis auxiliares para construir impacto_contrato
            total_loan_amount = parsed['valor_original_divida'] if parsed['valor_original_divida'] > 0 else parsed['valor_total_fatura']
        else:
            effective_installment = parsed['parcela']  # Usa input original do usuário
        

        financial_health = calc.compute_financial_health(
            income=parsed['renda'], 
            installment=effective_installment,  # ✅ Sempre usa valor mensal correto
            dependents_count=parsed['quantidade_dependentes'],
            valor_cesta_basica=parsed['valor_cesta_basica']
        )
        
        if parsed['eh_rotativo']:
            # Reutiliza variáveis já calculadas no bloco unificado acima
            contract_impact = {
                'valor_total_a_pagar': round(current_outstanding_balance, 2),
                'valor_total_emprestimo': round(total_loan_amount, 2),
                'custo_total_juros': round(projected_monthly_interest, 2),
                'quantidade_parcelas': 1,
                'observacao_rotativo': 'Valores referentes a UM mês de incidência de juros',
                'juros_mensal_projetado': round(projected_monthly_interest, 2),
                'pagamento_minimo_mensal': round(effective_installment, 2),  # ✅ Usa mesma variável
                'percentual_amortizacao': minimum_amortization_percentage * 100
            }
        else:
            # Parcelado: usa cálculo tradicional
            contract_impact = calc.compute_contract_impact(
                installment=effective_installment, 
                total_loan=parsed['valor_total_emprestimo'], 
                installments_count=parsed['quantidade_parcelas']
            )
        
        hidden_costs = calc.compute_hidden_costs(
            total_loan=parsed['valor_total_emprestimo'],
            user_rate_monthly=tax_metrics['mensal_consumidor'],
            installments_count=parsed['quantidade_parcelas'],
            actual_installment=effective_installment,  # ✅ Usa valor mensal correto
            serie_bcb=parsed['serie_bcb']
        )
        
        # calcular juros acumulados corretamente para rotativo vs parcelado
        if parsed['eh_rotativo']:
            # para rotativo: juros = quanto a dívida cresceu além do original
            accumulated_interest = parsed['valor_total_fatura'] - parsed['valor_original_divida']
            analyzed_original_debt = parsed['valor_original_divida'] if parsed['valor_original_divida'] > 0 else parsed['valor_total_emprestimo']
        else:
            # para parcelado: usar cálculo tradicional
            accumulated_interest = contract_impact['custo_total_juros']
            analyzed_original_debt = parsed['valor_total_emprestimo']
        
        # cálculo de percentual de juros sobre a dívida
        interest_cap = calc.check_interest_cap(
            original_debt=analyzed_original_debt,
            total_interest_paid=accumulated_interest,
            serie_bcb=parsed['serie_bcb']
        )
        
        analysis_json = {
            "eh_rotativo": parsed['eh_rotativo'],
            "data_contrato": parsed['data_contrato'],
            "serie_bcb": parsed['serie_bcb'],
            "metricas_taxas": tax_metrics,
            "saude_financeira": financial_health,
            "impacto_contrato": contract_impact,
            "analise_custos_ocultos": hidden_costs,
            "limite_juros_rotativos": interest_cap,
            "valor_cesta_basica": parsed['valor_cesta_basica']
        }

        summary = json.dumps(analysis_json, ensure_ascii=False)
        question = ANALYSIS_PROMPT_TEMPLATE.format(
            analysis_json=summary,
            data_contrato=parsed['data_contrato']
        )

        # Bedrock Agent Runtime com Knowledge Base
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

        return {
            "analysis_json": analysis_json,
            "ai_response": response["output"]["text"]
        }

    except Exception as e:
        raise Exception(f"Erro na análise completa: {str(e)}")