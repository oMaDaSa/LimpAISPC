def parse_debt_payload(data: dict) -> dict:
    if not data:
        raise ValueError("Payload vazio")
    
    # Taxa de mercado (obrigatória, o frontend que faz a req pro bcb)
    market_rate_annual = data.get('taxa_mercado_anual')
    if market_rate_annual is None:
        raise ValueError("Taxa de referência de mercado ausente (taxa_mercado_anual)")
    
    return {
        'rate_type': data.get('tipo_taxa'),
        'cet_rate': float(data.get('taxa_cet', 0.0)),
        'income': float(data.get('renda', 0.0)),
        'installment': float(data.get('parcela', 0.0)),
        'dependents_count': int(data.get('quantidade_dependentes', 0)),
        'total_loan': float(data.get('valor_total_emprestimo', 0.0)),
        'installments_count': int(data.get('quantidade_parcelas', 0)),
        'market_rate_annual': float(market_rate_annual)
    }
