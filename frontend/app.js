// Lógica de descrição dinâmica
const selectBcb = document.getElementById('serie_bcb');
const descSpan = document.getElementById('credit-desc');
selectBcb.addEventListener('change', function() {
    descSpan.innerText = this.options[this.selectedIndex].getAttribute('data-desc');
});

// Limitar data do contrato (BCB só tem dados com pelo menos 1 mês de atraso)
const dataContratoInput = document.querySelector('input[name="data_contrato"]');
const maxDate = new Date();
maxDate.setMonth(maxDate.getMonth() - 1);
dataContratoInput.max = maxDate.toISOString().split('T')[0];

// Configuração das Máscaras (IMask)
const moneyCfg = { mask: 'R$ num', blocks: { num: { mask: Number, thousandsSeparator: '.', radix: ',', scale: 2, padFractionalZeros: true, min: 0 } } };
const percentCfg = { mask: 'num%', lazy: false, blocks: { num: { mask: Number, radix: ',', scale: 2, min: 0, max: 99.99 } } };

const rendaMask = IMask(document.getElementById('renda_input'), moneyCfg);
const parcelaMask = IMask(document.getElementById('parcela_input'), moneyCfg);
const valorTotalEmprestimoMask = IMask(document.getElementById('valor_total_emprestimo_input'), moneyCfg);
const taxaMask = IMask(document.getElementById('taxa_input'), percentCfg);

// Dinâmica dos campos de contrato conforme modalidade
const groupValorTotal = document.getElementById('group_valor_total_emprestimo');
const groupParcelas = document.getElementById('group_quantidade_parcelas');
const valorTotalInput = document.getElementById('valor_total_emprestimo_input');
const parcelasInput = document.querySelector('input[name="quantidade_parcelas"]');

// Busca taxa de mercado do Banco Central
async function fetchMarketRate(serieBcb, dataContrato) {
    try {
        if (!serieBcb || !dataContrato) return null;

        const [year, month, day] = dataContrato.split('-');
        const date_start = `01/${month}/${year}`;
        const date_end = `28/${month}/${year}`;

        const response = await fetch(`https://api.bcb.gov.br/dados/serie/bcdata.sgs.${serieBcb}/dados?formato=json&dataInicial=${date_start}&dataFinal=${date_end}`);
        const data = await response.json();

        console.log('Resposta BCB:', data);

        if (data && data.length > 0) {
            // Retorna a taxa em formato decimal (ex: 23.82 = 23.82%)
            return parseFloat(data[0].valor);
        }
        return null;
    } catch (error) {
        console.error("Erro ao buscar taxa do BCB:", error);
        return null;
    }
}

function updateContractFields() {
    const mode = selectBcb.value;
    const revolving = ['20716', '20718'].includes(mode); // Cartão Rotativo, Cheque Especial

    if (revolving) {
        // Valor total pode ser 0 e parcelas 0 em dívidas rotativas
        valorTotalEmprestimoMask.unmaskedValue = '0';
        valorTotalInput.readOnly = true;
        valorTotalInput.required = false;
        groupValorTotal.classList.add('hidden');

        parcelasInput.value = '0';
        parcelasInput.readOnly = true;
        parcelasInput.required = false;
        groupParcelas.classList.add('hidden');
    } else {
        // Empréstimos/financiamentos: campos visíveis e editáveis
        valorTotalInput.readOnly = false;
        valorTotalInput.required = true;
        groupValorTotal.classList.remove('hidden');

        parcelasInput.readOnly = false;
        parcelasInput.required = true;
        groupParcelas.classList.remove('hidden');
    }
}

// Inicializa dinâmica
updateContractFields();
selectBcb.addEventListener('change', updateContractFields);

// Envio dos dados
document.getElementById('debtForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = document.getElementById('btnSubmit');
    const resultDiv = document.getElementById('result');
    
    btn.disabled = true;
    btn.innerText = "Processando Análise...";
    resultDiv.classList.add('hidden');

    const formData = new FormData(this);
    const rawData = Object.fromEntries(formData.entries());

    // Busca taxa de mercado do BCB
    const marketRate = await fetchMarketRate(rawData.serie_bcb, rawData.data_contrato);

    const data = {
        ...rawData,
        taxa_cet: parseFloat(taxaMask.unmaskedValue.replace(',', '.')),
        renda: parseFloat(rendaMask.unmaskedValue.replace(',', '.')),
        parcela: parseFloat(parcelaMask.unmaskedValue.replace(',', '.')),
        valor_total_emprestimo: parseFloat(valorTotalEmprestimoMask.unmaskedValue.replace(',', '.')),
        quantidade_parcelas: parseInt(rawData.quantidade_parcelas),
        quantidade_dependentes: parseInt(rawData.quantidade_dependentes),
        valor_cesta_basica: parseFloat(rawData.valor_cesta_basica),
        taxa_mercado_anual: marketRate
    };

    const [year, month, day] = rawData.data_contrato.split('-');
    data.data_contrato = `${day}/${month}/${year}`;

    // Printar JSON enviado
    console.log('JSON enviado para API:', JSON.stringify(data, null, 2));

    try {
        const response = await fetch('https://7z59i92b98.execute-api.us-east-1.amazonaws.com/api/debt-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        console.log('JSON recebido da API:', JSON.stringify(result, null, 2));
        if (result.status === "success") {
            // Preprocessar markdown: substituir \n escapado e adicionar quebras antes de ##
            let md = result.ai_response || '';
            // Substituir \n escapado por quebra real
            md = md.replace(/\\n/g, '\n');
            // Adicionar quebra dupla antes de ## que não têm quebra dupla
            md = md.replace(/([^\n])\n(##)/g, '$1\n\n$2');
            // Adicionar quebra dupla se ## vier direto após texto sem quebra
            md = md.replace(/([^\n])(##)/g, '$1\n\n$2');
            console.log('Markdown processado:', md);
            // Renderizar markdown para HTML bonito
            resultDiv.innerHTML = marked.parse(md);
            resultDiv.classList.remove('hidden');
            resultDiv.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        alert("Erro ao conectar com o servidor da AWS.");
    } finally {
        btn.disabled = false;
        btn.innerText = "Gerar Laudo Técnico e Jurídico";
    }
});
