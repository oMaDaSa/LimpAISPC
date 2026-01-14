class Calculator:
    def __init__(self):
        self.EXISTENTIAL_MIN = 600.0
        self.SECURITY_MARGIN = 35.0  # 35% da renda
        self.COST_PER_DEPENDENT = self.EXISTENTIAL_MIN / 2  # custo adicional por dependente

    def monthly_to_annual(self, monthly_rate: float) -> float:
        #taxa vem em porcentagem
        annual_rate = (1 + monthly_rate / 100) ** 12 - 1
        return round(annual_rate * 100, 2)

    def annual_to_monthly(self, anual_rate: float) -> float:
        #taxa vem em porcentagem
        monthly_rate = (1 + anual_rate / 100) ** (1 / 12) - 1
        return round(monthly_rate * 100, 2)

    def compute_rates(self, rate_type: str, cet_rate: float, market_rate_annual: float):
        market_rate_monthly = self.annual_to_monthly(market_rate_annual)
        if rate_type == 'anual':
            user_rate_monthly = self.annual_to_monthly(cet_rate)
            user_rate_annual = cet_rate
        else:
            user_rate_monthly = cet_rate
            user_rate_annual = self.monthly_to_annual(cet_rate)
        return user_rate_monthly, user_rate_annual, market_rate_monthly

    def compute_tax_metrics(self, rate_type: str, cet_rate: float, market_rate_annual: float, serie_bcb: str = '') -> dict:
        user_rate_monthly, user_rate_annual, market_rate_monthly = self.compute_rates(rate_type, cet_rate, market_rate_annual)
        #abuso de taxa
        tax_abuse = ((user_rate_monthly - market_rate_monthly) / market_rate_monthly) * 100
        
        result = {
            "mensal_consumidor": round(user_rate_monthly, 2),
            "anual_consumidor": round(user_rate_annual, 2),
            "mensal_mercado": round(market_rate_monthly, 2),
            "anual_mercado": round(market_rate_annual, 2),
            "percentual_abuso_taxa": round(tax_abuse, 2)
        }
        
        # verificação específica para Cheque Especial (Resolução CMN 4.765/2019 - limite 8% a.m.)
        if serie_bcb == '20718' and user_rate_monthly > 8.0:
            result["alerta_taxa_ilegal_cheque"] = True
            result["mensagem_taxa_ilegal"] = f"A taxa de {user_rate_monthly}% ao mês viola a Resolução CMN 4.765/2019 que limita o cheque especial a 8% ao mês."
        else:
            result["alerta_taxa_ilegal_cheque"] = False
            result["mensagem_taxa_ilegal"] = None
        
        return result

    def compute_financial_health(self, income: float, installment: float, dependents_count: int) -> dict:
        #saude financeira
        adjusted_existential_min = self.EXISTENTIAL_MIN + (dependents_count * self.COST_PER_DEPENDENT)
        commitment = (installment / income) * 100
        monthly_leftover = income - installment
        violates_minimum = monthly_leftover < adjusted_existential_min
        # renda per capita familiar após a parcela
        family_per_capita = monthly_leftover / (1 + dependents_count)
        return {
            "comprometimento_renda_pct": round(commitment, 2),
            "saldo_pos_parcela": round(monthly_leftover, 2),
            "renda_per_capita_familiar": round(family_per_capita, 2),
            "minimo_existencial_ajustado": adjusted_existential_min,
            "alerta_minimo_existencial": violates_minimum,
            "acima_margem_seguranca": commitment > self.SECURITY_MARGIN
        }

    def check_interest_cap(self, original_debt: float, total_interest_paid: float, serie_bcb: str) -> dict:
        #calcula percentual de juros e verifica se ultrapassa 100% (Lei do Desenrola - cartão rotativo 20716 e parcelado 20719)
        if original_debt > 0:
            interest_percentage = (total_interest_paid / original_debt) * 100
        else:
            interest_percentage = 0
        
        # verificação explícita: cartão rotativo (20716) e parcelado (20719) têm limite de 100%
        is_subject_to_cap = serie_bcb in ['20716', '20719']
        exceeds_100_percent = interest_percentage > 100
        
        # alerta apenas se for modalidade sujeita ao teto E ultrapassar 100%
        alert_limit_exceeded = is_subject_to_cap and exceeds_100_percent
        
        return {
            "percentual_juros_sobre_divida": round(interest_percentage, 2),
            "serie_bcb": serie_bcb,
            "sujeito_ao_teto_100_porcento": is_subject_to_cap,
            "juros_ultrapassam_100_porcento": alert_limit_exceeded
        }

    def compute_contract_impact(self, installment: float, total_loan: float, installments_count: int) -> dict:
        total_to_pay = installment * installments_count
        total_interest_cost = total_to_pay - total_loan
        return {
            "valor_total_a_pagar": round(total_to_pay, 2),
            "custo_total_juros": round(total_interest_cost, 2),
            "valor_total_emprestimo": round(total_loan, 2),
            "quantidade_parcelas": installments_count
        }

    def compute_hidden_costs(self, total_loan: float, user_rate_monthly: float, installments_count: int, actual_installment: float, serie_bcb: str) -> dict:
        # modalidades rotativas não têm parcela fixa calculável com tabela Price
        if serie_bcb in ['20716', '20718']:
            return {
                "parcela_teorica": None,
                "parcela_real": round(actual_installment, 2),
                "valor_taxas_embutidas_mensal": 0.0,
                "impacto_total_taxas_embutidas": 0.0,
            }

        i = user_rate_monthly / 100

        # fórmula da Tabela Price: PMT = PV * i / (1 - (1 + i)^-n)
        if i == 0:
            theoretical_installment = total_loan / installments_count
        else:
            theoretical_installment = total_loan * i / (1 - (1 + i) ** -installments_count)

        # diferença entre o que deveria ser cobrado e o que realmente é cobrado
        hidden_cost_monthly = actual_installment - theoretical_installment
        total_hidden_impact = hidden_cost_monthly * installments_count

        return {
            "parcela_teorica": round(theoretical_installment, 2),
            "parcela_real": round(actual_installment, 2),
            "valor_taxas_embutidas_mensal": round(hidden_cost_monthly, 2),
            "impacto_total_taxas_embutidas": round(total_hidden_impact, 2)
        }
