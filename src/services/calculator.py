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

    def compute_tax_metrics(self, rate_type: str, cet_rate: float, market_rate_annual: float) -> dict:
        user_rate_monthly, user_rate_annual, market_rate_monthly = self.compute_rates(rate_type, cet_rate, market_rate_annual)
        #abuso de taxa
        tax_abuse = ((user_rate_monthly - market_rate_monthly) / market_rate_monthly) * 100
        return {
            "mensal_consumidor": round(user_rate_monthly, 2),
            "anual_consumidor": round(user_rate_annual, 2),
            "mensal_mercado": round(market_rate_monthly, 2),
            "anual_mercado": round(market_rate_annual, 2),
            "percentual_abuso_taxa": round(tax_abuse, 2)
        }

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

    def compute_contract_impact(self, installment: float, total_loan: float, installments_count: int) -> dict:
        total_to_pay = installment * installments_count
        total_interest_cost = total_to_pay - total_loan
        return {
            "valor_total_a_pagar": round(total_to_pay, 2),
            "custo_total_juros": round(total_interest_cost, 2),
            "valor_total_emprestimo": round(total_loan, 2),
            "quantidade_parcelas": installments_count
        }
