/**
 * GestorBot - Análise Anual JavaScript
 * Lógica para o gráfico de evolução mensal (Meses x Valores)
 */

document.addEventListener('DOMContentLoaded', function () {
    if (typeof DADOS_ANUAIS === 'undefined') return;

    let chartAnual = null;
    let mostrarComparativo = false;
    let filtroAtual = 'AMBOS';

    /**
     * Inicializa o gráfico de evolução mensal
     */
    const inicializarGrafico = () => {
        renderizarGrafico(filtroAtual, mostrarComparativo);
        configurarFiltros();
    };

    /**
     * Renderiza o gráfico com os filtros aplicados
     */
    const renderizarGrafico = (filtro, comparar) => {
        const ctx = document.getElementById('grafico-anual').getContext('2d');

        if (chartAnual) {
            chartAnual.destroy();
        }

        const datasets = [];

        // Dataset Receitas ano atual
        if (filtro === 'AMBOS' || filtro === 'RECEITAS') {
            datasets.push({
                label: `Receitas ${DADOS_ANUAIS.ano}`,
                data: DADOS_ANUAIS.receitas,
                borderColor: '#198754',
                backgroundColor: 'rgba(25, 135, 84, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 8
            });

            // Comparativo ano anterior
            if (comparar) {
                datasets.push({
                    label: `Receitas ${DADOS_ANUAIS.anoAnterior}`,
                    data: DADOS_ANUAIS.receitasAnterior,
                    borderColor: 'rgba(25, 135, 84, 0.4)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5
                });
            }
        }

        // Dataset Despesas ano atual
        if (filtro === 'AMBOS' || filtro === 'DESPESAS') {
            datasets.push({
                label: `Despesas ${DADOS_ANUAIS.ano}`,
                data: DADOS_ANUAIS.despesas,
                borderColor: '#dc3545',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 8
            });

            // Comparativo ano anterior
            if (comparar) {
                datasets.push({
                    label: `Despesas ${DADOS_ANUAIS.anoAnterior}`,
                    data: DADOS_ANUAIS.despesasAnterior,
                    borderColor: 'rgba(220, 53, 69, 0.4)',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5
                });
            }
        }

        chartAnual = new Chart(ctx, {
            type: 'line',
            data: {
                labels: DADOS_ANUAIS.meses,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function (context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += new Intl.NumberFormat('pt-BR', {
                                        style: 'currency',
                                        currency: 'BRL'
                                    }).format(context.parsed.y);
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                return 'R$ ' + value.toLocaleString('pt-BR');
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    };

    /**
     * Configura os event listeners dos filtros
     */
    const configurarFiltros = () => {
        document.getElementById('btnAnualAmbos').addEventListener('change', () => {
            filtroAtual = 'AMBOS';
            renderizarGrafico(filtroAtual, mostrarComparativo);
        });

        document.getElementById('btnAnualReceitas').addEventListener('change', () => {
            filtroAtual = 'RECEITAS';
            renderizarGrafico(filtroAtual, mostrarComparativo);
        });

        document.getElementById('btnAnualDespesas').addEventListener('change', () => {
            filtroAtual = 'DESPESAS';
            renderizarGrafico(filtroAtual, mostrarComparativo);
        });

        document.getElementById('btnCompararAnterior').addEventListener('change', (e) => {
            mostrarComparativo = e.target.checked;
            renderizarGrafico(filtroAtual, mostrarComparativo);
        });
    };

    /**
     * Renderiza gráfico de barras horizontais para Top 5 Despesas
     */
    const renderizarRankingDespesas = () => {
        const canvas = document.getElementById('grafico-ranking-despesas');
        if (!canvas || !DADOS_ANUAIS.rankingDespesas || DADOS_ANUAIS.rankingDespesas.length === 0) return;

        const ctx = canvas.getContext('2d');
        const labels = DADOS_ANUAIS.rankingDespesas.map(item => item.categoria);
        const valores = DADOS_ANUAIS.rankingDespesas.map(item => item.valor);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Despesas',
                    data: valores,
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.8)',
                        'rgba(220, 53, 69, 0.65)',
                        'rgba(220, 53, 69, 0.5)',
                        'rgba(220, 53, 69, 0.35)',
                        'rgba(220, 53, 69, 0.2)'
                    ],
                    borderColor: '#dc3545',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return new Intl.NumberFormat('pt-BR', {
                                    style: 'currency',
                                    currency: 'BRL'
                                }).format(context.parsed.x);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                return 'R$ ' + (value / 1000).toFixed(0) + 'k';
                            }
                        }
                    }
                }
            }
        });
    };

    /**
     * Renderiza gráfico de barras horizontais para Top 5 Receitas
     */
    const renderizarRankingReceitas = () => {
        const canvas = document.getElementById('grafico-ranking-receitas');
        if (!canvas || !DADOS_ANUAIS.rankingReceitas || DADOS_ANUAIS.rankingReceitas.length === 0) return;

        const ctx = canvas.getContext('2d');
        const labels = DADOS_ANUAIS.rankingReceitas.map(item => item.categoria);
        const valores = DADOS_ANUAIS.rankingReceitas.map(item => item.valor);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Receitas',
                    data: valores,
                    backgroundColor: [
                        'rgba(25, 135, 84, 0.8)',
                        'rgba(25, 135, 84, 0.65)',
                        'rgba(25, 135, 84, 0.5)',
                        'rgba(25, 135, 84, 0.35)',
                        'rgba(25, 135, 84, 0.2)'
                    ],
                    borderColor: '#198754',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return new Intl.NumberFormat('pt-BR', {
                                    style: 'currency',
                                    currency: 'BRL'
                                }).format(context.parsed.x);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function (value) {
                                return 'R$ ' + (value / 1000).toFixed(0) + 'k';
                            }
                        }
                    }
                }
            }
        });
    };

    // Inicializa todos os gráficos
    inicializarGrafico();
    renderizarRankingDespesas();
    renderizarRankingReceitas();
});
