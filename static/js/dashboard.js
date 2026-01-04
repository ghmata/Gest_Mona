/**
 * Dashboard JavaScript - GestorBot
 * 
 * Este módulo contém a lógica JavaScript do dashboard:
 * - Renderização de gráficos Chart.js
 * - Filtro de categorias por tipo
 * - Paginação
 * - Mini dashboard de subcategorias
 * 
 * @author GestorBot Team
 * @version 1.1.0
 */

'use strict';

// =============================================================================
// CONFIGURAÇÃO DE CORES
// =============================================================================

/**
 * Cores por categoria PRINCIPAL de DESPESA
 */
const CORES_DESPESAS = {
    'Insumos': '#28a745',
    'Bebidas': '#ffc107',
    'Operacional': '#17a2b8',
    'Pessoal': '#5c6bc0',
    'Infraestrutura': '#8d6e63',
    'Administrativo': '#455a64',
    'Marketing e Eventos': '#651fff',
    'Outros': '#6c757d'
};

/**
 * Cores por SUBCATEGORIA de DESPESA (para mini dashboard)
 * Paleta com cores vivas e facilmente identificáveis - SEM REPETIÇÕES
 */
const CORES_SUBCATEGORIAS = {
    // Insumos - tons variados e vibrantes
    'Frutos do Mar': '#00D4FF',      // Ciano brilhante
    'Carnes e Aves': '#FF4757',      // Vermelho vivo
    'Hortifruti': '#2ED573',         // Verde esmeralda
    'Laticínios': '#FFA502',         // Laranja dourado
    'Frutas': '#FF6B81',             // Rosa coral
    'Alimento (Variado)': '#A55EEA', // Roxo vibrante
    'Gelo': '#70A1FF',               // Azul gelo

    // Bebidas - tons quentes e frios alternados
    'Bebidas': '#FFD93D',            // Amarelo dourado
    'Cervejas': '#FF9F43',           // Laranja cerveja
    'Destilados': '#9B59B6',         // Roxo profundo
    'Vinhos': '#E91E63',             // Magenta vinho
    'Energético': '#FF5252',         // Vermelho energético

    // Operacional - tons azuis e neutros
    'Embalagens': '#54A0FF',         // Azul celeste
    'Limpeza': '#00CEC9',            // Turquesa
    'Manutenção': '#F39C12',         // Amarelo mostarda
    'Gás': '#E74C3C',                // Vermelho fogo
    'Organização': '#EC407A',        // Rosa pink (corrigido)

    // Pessoal - paleta vibrante e diversificada
    'Pessoal': '#3498DB',            // Azul brilhante
    'Pro Labore': '#E74C3C',         // Vermelho intenso
    'Salário': '#27AE60',            // Verde vibrante
    'Freelancer': '#F39C12',         // Laranja ouro
    'Gorjeta': '#9B59B6',            // Roxo vivo
    'Venda de Férias': '#1ABC9C',    // Verde água
    'Venda de Folga': '#E67E22',     // Laranja cenoura
    'Vale Transporte': '#3498DB',    // Azul céu
    'Vale Refeição': '#E91E63',      // Rosa magenta

    // Infraestrutura - tons terrosos
    'Aluguel': '#D35400',            // Laranja queimado
    'Energia': '#F1C40F',            // Amarelo elétrico
    'Seguros': '#16A085',            // Verde petróleo (corrigido)

    // Administrativo - tons de cinza e azul
    'Impostos': '#576574',           // Cinza azulado
    'Transporte': '#10AC84',         // Verde floresta

    // Marketing e Eventos - tons vibrantes
    'Eventos': '#B33771',            // Magenta escuro
    'Marketing': '#00B894',          // Verde menta

    // Comum
    'Outros': '#95A5A6',             // Cinza médio
    'Sem subcategoria': '#BDC3C7'    // Cinza claro
};

/**
 * Cores por categoria de RECEITA
 */
const CORES_RECEITAS = {
    'Vendas': '#198754',
    'PIX': '#20c997',
    'Cartão': '#0d6efd',
    'Transferência': '#6610f2',
    'Outros': '#6c757d'
};

// =============================================================================
// GRÁFICOS
// =============================================================================

/**
 * Configuração padrão para gráficos donut
 */
const CHART_OPTIONS = {
    responsive: true,
    maintainAspectRatio: true,
    cutout: '60%',
    plugins: {
        legend: { display: false },
        tooltip: {
            callbacks: {
                label: (context) => {
                    const value = context.raw;
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = ((value / total) * 100).toFixed(1);
                    return ` R$ ${value.toFixed(2)} (${percentage}%)`;
                }
            }
        }
    }
};

/**
 * Renderiza gráfico de despesas por categoria
 * @param {string} canvasId - ID do elemento canvas
 * @param {Object} dados - Dados das despesas {categoria: valor}
 */
const renderizarGraficoDespesas = (canvasId, dados) => {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !dados || Object.keys(dados).length === 0) return;

    const ctx = canvas.getContext('2d');
    const labels = Object.keys(dados);
    const valores = Object.values(dados);
    const cores = labels.map(cat => CORES_DESPESAS[cat] || '#6c757d');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: cores,
                borderWidth: 3,
                borderColor: '#fff',
                hoverBorderWidth: 0
            }]
        },
        options: CHART_OPTIONS
    });
};

/**
 * Renderiza gráfico de receitas por categoria
 * @param {string} canvasId - ID do elemento canvas
 * @param {Object} dados - Dados das receitas {categoria: valor}
 */
const renderizarGraficoReceitas = (canvasId, dados) => {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !dados || Object.keys(dados).length === 0) return;

    const ctx = canvas.getContext('2d');
    const labels = Object.keys(dados);
    const valores = Object.values(dados);
    const cores = labels.map(cat => CORES_RECEITAS[cat] || '#198754');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: cores,
                borderWidth: 3,
                borderColor: '#fff',
                hoverBorderWidth: 0
            }]
        },
        options: CHART_OPTIONS
    });
};

// =============================================================================
// PAGINAÇÃO
// =============================================================================

/**
 * Inicializa seletor de itens por página
 */
const inicializarPaginacao = () => {
    const perPageSelect = document.getElementById('perPageSelect');
    if (!perPageSelect) return;

    perPageSelect.addEventListener('change', () => {
        const perPage = perPageSelect.value;
        const url = new URL(window.location.href);
        url.searchParams.set('per_page', perPage);
        url.searchParams.set('page', '1');
        url.hash = 'transacoes';
        window.location.href = url.toString();
    });
};

// =============================================================================
// FILTROS
// =============================================================================

/**
 * Categorias de receita (para filtro)
 */
const CATEGORIAS_RECEITA = ['Vendas', 'Caixa', 'PIX', 'Cartão', 'Transferência', 'Outros'];

/**
 * Atualiza visibilidade das categorias baseado no tipo selecionado
 */
const atualizarCategorias = () => {
    const filtroTipo = document.getElementById('filtroTipo');
    const filtroCategoria = document.getElementById('filtroCategoria');
    const optDespesas = document.getElementById('optDespesas');
    const optReceitas = document.getElementById('optReceitas');

    if (!filtroTipo || !optDespesas || !optReceitas) return;

    const tipo = filtroTipo.value;

    if (tipo === 'DESPESA') {
        optDespesas.style.display = '';
        optReceitas.style.display = 'none';
        // Limpa se categoria atual é de receita
        if (CATEGORIAS_RECEITA.includes(filtroCategoria?.value)) {
            filtroCategoria.value = '';
        }
    } else if (tipo === 'RECEITA') {
        optDespesas.style.display = 'none';
        optReceitas.style.display = '';
        // Limpa se categoria atual é de despesa
        if (filtroCategoria?.value && !CATEGORIAS_RECEITA.includes(filtroCategoria.value) && filtroCategoria.value !== '') {
            filtroCategoria.value = '';
        }
    } else {
        // Mostra todos
        optDespesas.style.display = '';
        optReceitas.style.display = '';
    }
};

/**
 * Inicializa filtro de categorias
 */
const inicializarFiltros = () => {
    const filtroTipo = document.getElementById('filtroTipo');
    if (!filtroTipo) return;

    filtroTipo.addEventListener('change', atualizarCategorias);
    atualizarCategorias(); // Aplicar no load
};

// =============================================================================
// INICIALIZAÇÃO
// =============================================================================

/**
 * Inicializa dashboard quando DOM estiver pronto
 */
const inicializarDashboard = () => {
    // Inicializar gráficos via data attributes
    const graficoDespesas = document.getElementById('grafico-despesas');
    if (graficoDespesas) {
        const dadosStr = graficoDespesas.dataset.valores;
        if (dadosStr) {
            try {
                const dados = JSON.parse(dadosStr);
                renderizarGraficoDespesas('grafico-despesas', dados);
            } catch (e) {
                console.error('Erro ao parsear dados de despesas:', e);
            }
        }
    }

    const graficoReceitas = document.getElementById('grafico-receitas');
    if (graficoReceitas) {
        const dadosStr = graficoReceitas.dataset.valores;
        if (dadosStr) {
            try {
                const dados = JSON.parse(dadosStr);
                renderizarGraficoReceitas('grafico-receitas', dados);
            } catch (e) {
                console.error('Erro ao parsear dados de receitas:', e);
            }
        }
    }

    // Inicializar paginação
    inicializarPaginacao();

    // Inicializar filtros
    inicializarFiltros();

    // Inicializar mini dashboard de subcategorias
    inicializarMiniDashboard();
};

// Iniciar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', inicializarDashboard);

// =============================================================================
// MINI DASHBOARD DE SUBCATEGORIAS
// =============================================================================

/**
 * Gráfico atual do mini dashboard (para destruir antes de recriar)
 */
let chartMiniDashboard = null;

/**
 * Inicializa eventos de clique para abrir mini dashboard
 */
const inicializarMiniDashboard = () => {
    // Adiciona evento de clique nas categorias da lista
    document.querySelectorAll('.categoria-clicavel').forEach(item => {
        item.addEventListener('click', async function () {
            const categoria = this.dataset.categoria;
            if (categoria) {
                await carregarMiniDashboard(categoria);
            }
        });
    });
};

/**
 * Carrega dados de subcategorias via API e exibe mini dashboard
 * @param {string} categoria - Nome da categoria principal
 */
const carregarMiniDashboard = async (categoria) => {
    const container = document.getElementById('mini-dashboard-container');
    const titulo = document.getElementById('mini-dashboard-titulo');
    const loading = document.getElementById('mini-dashboard-loading');
    const conteudo = document.getElementById('mini-dashboard-conteudo');

    if (!container) return;

    // Mostra container e loading
    container.style.display = 'block';
    titulo.textContent = `Detalhamento: ${categoria}`;
    loading.style.display = 'block';
    conteudo.style.display = 'none';

    try {
        // Obtem mês/ano da URL atual
        const urlParams = new URLSearchParams(window.location.search);
        const mes = urlParams.get('mes') || new Date().getMonth() + 1;
        const ano = urlParams.get('ano') || new Date().getFullYear();

        // Busca dados via API
        const response = await fetch(`/api/gastos-subcategoria?categoria=${encodeURIComponent(categoria)}&mes=${mes}&ano=${ano}`);
        const data = await response.json();

        if (data.sucesso) {
            renderizarMiniDashboard(data.gastos_por_subcategoria, categoria);
        } else {
            conteudo.innerHTML = `<p class="text-danger">${data.erro || 'Erro ao carregar dados.'}</p>`;
        }
    } catch (error) {
        console.error('Erro ao carregar mini dashboard:', error);
        conteudo.innerHTML = '<p class="text-danger">Erro de conexão.</p>';
    } finally {
        loading.style.display = 'none';
        conteudo.style.display = 'block';
    }
};

/**
 * Renderiza o mini dashboard com gráfico e lista de subcategorias
 * @param {Object} dados - Dados de gastos por subcategoria
 * @param {string} categoria - Nome da categoria principal
 */
const renderizarMiniDashboard = (dados, categoria) => {
    const conteudo = document.getElementById('mini-dashboard-conteudo');
    const canvas = document.getElementById('grafico-subcategorias');

    if (!conteudo || Object.keys(dados).length === 0) {
        conteudo.innerHTML = '<p class="text-muted text-center">Nenhuma subcategoria registrada.</p>';
        return;
    }

    // Destrói gráfico anterior se existir
    if (chartMiniDashboard) {
        chartMiniDashboard.destroy();
    }

    // Renderiza lista de subcategorias
    const lista = document.getElementById('lista-subcategorias');
    if (lista) {
        lista.innerHTML = Object.entries(dados)
            .sort((a, b) => b[1] - a[1])
            .map(([subcat, valor]) => `
                <li class="list-group-item d-flex justify-content-between align-items-center py-1">
                    <span class="d-flex align-items-center">
                        <span class="badge-dot me-2" style="background-color: ${CORES_SUBCATEGORIAS[subcat] || '#6c757d'};"></span>
                        ${subcat}
                    </span>
                    <strong class="text-danger">R$ ${valor.toFixed(2)}</strong>
                </li>
            `).join('');
    }

    // Renderiza gráfico
    if (canvas) {
        const ctx = canvas.getContext('2d');
        const labels = Object.keys(dados);
        const valores = Object.values(dados);
        const cores = labels.map(subcat => CORES_SUBCATEGORIAS[subcat] || '#6c757d');

        chartMiniDashboard = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: valores,
                    backgroundColor: cores,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '55%',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.raw;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return ` R$ ${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
};

/**
 * Fecha o mini dashboard
 */
const fecharMiniDashboard = () => {
    const container = document.getElementById('mini-dashboard-container');
    if (container) {
        container.style.display = 'none';
    }
};
