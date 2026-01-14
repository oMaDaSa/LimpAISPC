def parse_debt_payload(data: dict) -> dict:
    if not data:
        raise ValueError("Payload vazio")
    
    # Taxa de mercado (obrigatória, o frontend que faz a req pro bcb)
    market_rate_annual = data.get('taxa_mercado_anual')
    if market_rate_annual is None:
        raise ValueError("Taxa de referência de mercado ausente (taxa_mercado_anual)")
    
    serie_bcb = data.get('serie_bcb', '')
    is_revolving = serie_bcb in ['20716', '20718']
    
    # Captura valores específicos para rotativo
    invoice_total = float(data.get('valor_total_fatura', 0.0))
    original_debt = float(data.get('valor_original_divida', 0.0))
    installment = float(data.get('parcela', 0.0))
    total_loan = float(data.get('valor_total_emprestimo', 0.0))
    
    # Lógica de Saldo Devedor para Rotativo
    if is_revolving:
        # Tenta pegar valor da fatura, se não tiver, usa o total_loan padrão
        base_value = invoice_total if invoice_total > 0 else total_loan
        
        if base_value > 0:
            # Se pagou algo (installment), subtrai. Se não pagou nada (installment=0), deve tudo.
            outstanding_balance = base_value - installment
            total_loan = outstanding_balance if outstanding_balance > 0 else 0.0
    
    # Para rotativos, forçar quantidade_parcelas como 1 para cálculos mensais
    installments_count = int(data.get('quantidade_parcelas', 0))
    if is_revolving and installments_count == 0:
        installments_count = 1
    
    return {
        'tipo_taxa': data.get('tipo_taxa'),
        'taxa_cet': float(data.get('taxa_cet', 0.0)),
        'renda': float(data.get('renda', 0.0)),
        'parcela': installment,
        'quantidade_dependentes': int(data.get('quantidade_dependentes', 0)),
        'valor_total_emprestimo': total_loan,
        'quantidade_parcelas': installments_count,
        'taxa_mercado_anual': float(market_rate_annual),
        'valor_cesta_basica': float(data.get('valor_cesta_basica', 0.0)),
        'serie_bcb': serie_bcb,
        'eh_rotativo': is_revolving,
        'data_contrato': data.get('data_contrato', ''),
        'valor_total_fatura': invoice_total,
        'valor_original_divida': original_debt
    }
