from bcb_rates import get_bcb_rate

class Calculator:
    def init(self):
        self.EXISTENCIAL_MIN = 600.0
        self.SECURITY_MARGIN = 35.0 # 35% da renda

    def monthly_to_annual(self, monthly_rate: float) -> float:
        #taxa vem em porcentagem
        annual_rate = (1 + monthly_rate/100) ** 12 - 1
        return round(annual_rate * 100, 2)

    def annual_to_monthly(self, anual_rate: float) -> float:
        #taxa vem em porcentagem
        monthly_rate = (1 + anual_rate/100) ** (1/12) - 1
        return round(monthly_rate * 100, 2)
    
    def analysis(self, data: dict, market_rate_annual: float) -> dict:

        market_rate_monthly = self.convert_annual_to_monthly(market_rate_annual)
        
        if data['tipo_taxa'] == 'anual':
            user_rate_monthly = self.convert_annual_to_monthly(data['taxa_cet'])
            user_rate_annual = data['taxa_cet']
        else:
            user_rate_monthly = data['taxa_cet']
            user_rate_annual = self.convert_monthly_to_annual(data['taxa_cet'])

        #abuso de taxa
        tax_abuse = ((user_rate_monthly - market_rate_monthly) / market_rate_monthly) * 100

        #saude financeira
        commitment = (data['parcela'] / data['renda']) * 100
        monthly_leftover = data['renda'] - data['parcela']
        violates_minimum = monthly_leftover < self.EXISTENCIAL_MIN

        return {
            "tax_metrics": {
                "user_monthly": round(user_rate_monthly, 2),
                "user_annual": round(user_rate_annual, 2),
                "market_monthly": round(market_rate_monthly, 2),
                "market_annual": round(market_rate_annual, 2),
                "tax_abuse_percent": round(tax_abuse, 2)
            },
            "financial_health": {
                "income_commitment_pct": round(commitment, 2),
                "leftover_after_installment": round(monthly_leftover, 2),
                "existential_minimum_alert": violates_minimum,
                "above_security_margin": commitment > self.SECURITY_MARGIN
            }
        }