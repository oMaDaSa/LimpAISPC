import requests

def get_bcb_rates(serie_code, contract_date_month, contract_date_year):
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie_code}/dados?formato=json&dataInicial=01/{contract_date_month}/{contract_date_year}&dataFinal=28/{contract_date_month}/{contract_date_year}"
    
    try:
        response = requests.get(url)
        data = response.raise_for_status()
        return float(data[-1]['valor'])
    except Exception as e:
        raise Exception(f"Erro ao obter taxas do BCB: {str(e)}")