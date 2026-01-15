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
    const installment_plan = mode === '20719'; // Cartão Parcelado

    const labelParcela = document.getElementById('label_parcela');
    const helpParcela = document.getElementById('help_parcela');
    const labelValorTotal = document.getElementById('label_valor_total_emprestimo');

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

        // Mudar label para rotativos
        labelParcela.innerText = 'Valor pago na última fatura:';
        helpParcela.innerText = 'Informe o valor total pago na última fatura do cartão ou cheque especial. O rotativo só pode durar 30 dias, após esse prazo deve ser convertido em parcelado.';
    } else if (installment_plan) {
        // Cartão Parcelado: mostra campos padrão de empréstimo
        valorTotalInput.readOnly = false;
        valorTotalInput.required = true;
        groupValorTotal.classList.remove('hidden');
        labelValorTotal.innerText = 'Valor da Fatura que foi Parcelada:';

        parcelasInput.readOnly = false;
        parcelasInput.required = true;
        groupParcelas.classList.remove('hidden');

        // Label específico para parcelado
        labelParcela.innerText = 'Valor da Parcela Mensal:';
        helpParcela.innerText = 'Valor de cada parcela mensal da sua fatura parcelada.';
    } else {
        // Empréstimos/financiamentos padrão: campos visíveis e editáveis
        valorTotalInput.readOnly = false;
        valorTotalInput.required = true;
        groupValorTotal.classList.remove('hidden');
        labelValorTotal.innerText = 'Valor Total do Empréstimo:';

        parcelasInput.readOnly = false;
        parcelasInput.required = true;
        groupParcelas.classList.remove('hidden');

        // Restaurar label original
        labelParcela.innerText = 'Valor da Parcela Mensal:';
        helpParcela.innerText = 'Quanto sai do seu bolso todos os meses para pagar este contrato específico.';
    }
}

// Função para verificar se passou 30 dias desde a data do contrato
function checkThirtyDays(dataContrato, serieBcb) {
    if (!dataContrato || !['20716', '20718'].includes(serieBcb)) {
        return null;
    }
    
    const [year, month, day] = dataContrato.split('-');
    const contractDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    const today = new Date();
    const diffTime = today - contractDate;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays > 30) {
        if (serieBcb === '20716') {
            return {
                tipo: 'cartao',
                dias: diffDays,
                mensagem: `⚠️ Dívida no cartão de crédito rotativo há mais de ${diffDays} dias. Segundo a Resolução CMN 4.549/2017, o crédito rotativo só pode ser utilizado por até 30 dias. Após esse prazo, o banco é OBRIGADO a oferecer a conversão da dívida em parcelamento, com condições mais vantajosas.`
            };
        } else if (serieBcb === '20718') {
            return {
                tipo: 'cheque',
                dias: diffDays,
                mensagem: `⚠️ Seu cheque especial está sendo usado há mais de ${diffDays} dias. Segundo a Resolução CMN 4.765/2019, após 30 dias o banco DEVE OFERTAR uma linha de crédito para quitação do saldo devedor, geralmente parcelada. Essa oferta pode ser recusada.`
            };
        }
    }
    
    return null;
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

    const serie = rawData.serie_bcb;
    const valorCampoPrincipal = parseFloat(valorTotalEmprestimoMask.unmaskedValue.replace(',', '.')) || 0;
    const parcelaValor = parseFloat(parcelaMask.unmaskedValue.replace(',', '.')) || 0;
    const rendaValor = parseFloat(rendaMask.unmaskedValue.replace(',', '.')) || 0;
    const taxaCetValor = parseFloat(taxaMask.unmaskedValue.replace(',', '.')) || 0;
    const valorOriginalDividaInput = parseFloat(rawData.valor_original_divida || 0) || 0;

    // Valores padrão
    let valor_total_emprestimo = valorCampoPrincipal;
    let valor_total_fatura = valorCampoPrincipal;
    let valor_original_divida = valorOriginalDividaInput;
    let quantidade_parcelas = parseInt(rawData.quantidade_parcelas) || 0;

    if (serie === '20718') {
        // Cheque Especial: usar o valor principal digitado como fatura/emprestimo/divida original
        const base = valorCampoPrincipal || valorOriginalDividaInput || parcelaValor;
        valor_total_fatura = base;
        valor_total_emprestimo = base;
        valor_original_divida = base;
        quantidade_parcelas = 1; // evitar zero em cálculos
    } else if (serie === '20716') {
        // Cartão Rotativo: usar valor da fatura; se não tiver, cair para original/divida ou parcela
        const base = valorCampoPrincipal || valorOriginalDividaInput || parcelaValor;
        valor_total_fatura = base;
        valor_total_emprestimo = base;
        valor_original_divida = valorOriginalDividaInput || base;
        quantidade_parcelas = 1; // cálculo mensal para rotativo
    }

    // Fallback de segurança: se ainda zero e usuário digitou parcela, usar a parcela como base mínima
    if (!valor_total_emprestimo && parcelaValor) {
        valor_total_emprestimo = parcelaValor;
    }
    if (!valor_total_fatura && valor_total_emprestimo) {
        valor_total_fatura = valor_total_emprestimo;
    }
    if (!valor_original_divida && valor_total_emprestimo) {
        valor_original_divida = valor_total_emprestimo;
    }

    const data = {
        ...rawData,
        taxa_cet: taxaCetValor,
        renda: rendaValor,
        parcela: parcelaValor,
        valor_total_emprestimo,
        valor_total_fatura,
        valor_original_divida,
        quantidade_parcelas,
        quantidade_dependentes: parseInt(rawData.quantidade_dependentes),
        valor_cesta_basica: parseFloat(rawData.valor_cesta_basica),
        taxa_mercado_anual: marketRate
    };

    const [year, month, day] = rawData.data_contrato.split('-');
    data.data_contrato = `${day}/${month}/${year}`;

    // Verificar alerta de 30 dias no frontend
    const alerta30Dias = checkThirtyDays(rawData.data_contrato, rawData.serie_bcb);
    if (alerta30Dias) {
        const showAlert = confirm(alerta30Dias.mensagem + '\n\nDeseja continuar com a análise?');
        if (!showAlert) {
            btn.disabled = false;
            btn.innerText = "Gerar Laudo";
            return;
        }
    }

    // Printar JSON enviado
    console.log('JSON enviado para API:', JSON.stringify(data, null, 2));

    // Adicionar senha ao payload
    const password = document.getElementById('password_input').value;
    data.password = password;

    try {
        const response = await fetch('https://7z59i92b98.execute-api.us-east-1.amazonaws.com/api/debt-analysis', {
        //const response = await fetch('http://localhost:5000/api/debt-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        console.log('JSON recebido da API:', JSON.stringify(result, null, 2));
        
        if (result.error === "Senha incorreta") {
            alert("❌ Senha incorreta. Verifique a senha e tente novamente.");
        } else if (result.error) {
            alert("Erro: " + result.error);
        } else if (result.status === "success") {
            console.log('JSON enviado para LLM:', JSON.stringify(result.analysis_json, null, 2));
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
        btn.innerText = "Gerar Laudo";
    }
});
