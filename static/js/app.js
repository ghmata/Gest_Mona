/**
 * GestorBot - JavaScript Principal
 * Lógica para upload de notas, OCR e gestão de transações
 * Suporta imagens (JPG, PNG, etc.) e PDFs
 */

document.addEventListener('DOMContentLoaded', function () {
    // =========================================
    // Elementos da página Home
    // =========================================
    const btnNovaDespesa = document.getElementById('btn-nova-despesa');
    const btnNovaReceita = document.getElementById('btn-nova-receita');
    const inputCamera = document.getElementById('input-camera');
    const modalLoading = document.getElementById('modal-loading');
    const modalConferencia = document.getElementById('modal-conferencia');
    const modalSucesso = document.getElementById('modal-sucesso');
    const btnConfirmar = document.getElementById('btn-confirmar');
    const formConferencia = document.getElementById('form-conferencia');
    const imgPreview = document.getElementById('img-preview');
    const pdfPreview = document.getElementById('pdf-preview');
    const pdfNome = document.getElementById('pdf-nome');

    // Modal de escolha de modo
    const modalEscolhaModo = document.getElementById('modal-escolha-modo');
    const btnModoUnico = document.getElementById('btn-modo-unico');
    const btnModoMassa = document.getElementById('btn-modo-massa');

    // Se não estiver na home, não executar lógica de upload
    if (!btnNovaDespesa) return;

    // Bootstrap Modals
    const loadingModal = new bootstrap.Modal(modalLoading);
    const conferenciaModal = new bootstrap.Modal(modalConferencia);
    const sucessoModal = new bootstrap.Modal(modalSucesso);
    const escolhaModoModal = new bootstrap.Modal(modalEscolhaModo);

    // Tipo atual selecionado (DESPESA ou RECEITA)
    let tipoAtual = 'DESPESA';

    // =========================================
    // Mapeamento de Categorias e Subcategorias
    // =========================================
    const CATEGORIAS_SUBCATEGORIAS = {
        'Insumos': [
            { value: 'Frutos do Mar', label: '🦐 Frutos do Mar' },
            { value: 'Carnes e Aves', label: '🥩 Carnes e Aves' },
            { value: 'Hortifruti', label: '🥬 Hortifruti' },
            { value: 'Laticínios', label: '🧀 Laticínios' },
            { value: 'Frutas', label: '🍎 Frutas' },
            { value: 'Alimento (Variado)', label: '🥘 Alimento (Variado)' },
            { value: 'Gelo', label: '🧊 Gelo' },
            { value: 'Outros', label: '📋 Outros' }
        ],
        'Bebidas': [
            { value: 'Bebidas', label: '🥤 Bebidas' },
            { value: 'Cervejas', label: '🍺 Cervejas' },
            { value: 'Destilados', label: '🍸 Destilados' },
            { value: 'Vinhos', label: '🍾 Vinhos' },
            { value: 'Energético', label: '⚡ Energético' },
            { value: 'Outros', label: '📋 Outros' }
        ],
        'Operacional': [
            { value: 'Embalagens', label: '📦 Embalagens' },
            { value: 'Limpeza', label: '🧹 Limpeza' },
            { value: 'Manutenção', label: '🔧 Manutenção' },
            { value: 'Gás', label: '🔥 Gás' },
            { value: 'Organização', label: '📁 Organização' },
            { value: 'Outros', label: '📋 Outros' }
        ],
        'Pessoal': [
            { value: 'Pessoal', label: '👥 Pessoal' },
            { value: 'Pro Labore', label: '💼 Pro Labore' },
            { value: 'Salário', label: '💰 Salário' },
            { value: 'Freelancer', label: '🧑‍💻 Freelancer' },
            { value: 'Gorjeta', label: '💵 Gorjeta' },
            { value: 'Venda de Férias', label: '🏖️ Venda de Férias' },
            { value: 'Venda de Folga', label: '📅 Venda de Folga' },
            { value: 'Vale Transporte', label: '🚌 Vale Transporte' },
            { value: 'Vale Refeição', label: '🍽️ Vale Refeição' },
            { value: 'Outros', label: '📋 Outros' }
        ],
        'Infraestrutura': [
            { value: 'Aluguel', label: '🏠 Aluguel' },
            { value: 'Energia', label: '💡 Energia' },
            { value: 'Seguros', label: '🛡️ Seguros' },
            { value: 'Outros', label: '📋 Outros' }
        ],
        'Administrativo': [
            { value: 'Impostos', label: '🏛️ Impostos' },
            { value: 'Transporte', label: '🚚 Transporte' },
            { value: 'Outros', label: '📋 Outros' }
        ],
        'Marketing e Eventos': [
            { value: 'Eventos', label: '🎉 Eventos' },
            { value: 'Marketing', label: '📢 Marketing' },
            { value: 'Aluguel', label: '🏠 Aluguel' },
            { value: 'Outros', label: '📋 Outros' }
        ],
        'Outros': [
            { value: 'Outros', label: '📋 Outros' }
        ]
    };

    // =========================================
    // Mapeamento de Nomes de Arquivo → Categoria/Subcategoria
    // Detecta automaticamente baseado em padrões no nome do arquivo
    // =========================================
    const MAPEAMENTO_NOMES_ARQUIVO = [
        // Vendas / Caixa / PIX
        { regex: /pag\s*free|pagfree|pag\s*seguro|pagseguro/i, categoria: 'Administrativo', subcategoria: 'Outros' },
        { regex: /volga|vendas?\s*volga/i, categoria: 'Administrativo', subcategoria: 'Outros' },
        { regex: /getnet|cielo|rede|stone|sumup|mercado\s*pago/i, categoria: 'Administrativo', subcategoria: 'Outros' },
        { regex: /pix|transferencia|ted|doc/i, categoria: 'Administrativo', subcategoria: 'Outros' },
        { regex: /caixa|vendas|venda/i, categoria: 'Administrativo', subcategoria: 'Outros' },

        // Fornecedores de Alimentos
        { regex: /peixaria|peixe|pescado|frutos?\s*do\s*mar|camar[aã]o/i, categoria: 'Insumos', subcategoria: 'Frutos do Mar' },
        { regex: /açougue|a[cç]ougue|carne|frango|boi/i, categoria: 'Insumos', subcategoria: 'Carnes e Aves' },
        { regex: /hortifruti|hortifrutti|verdura|legume|salada/i, categoria: 'Insumos', subcategoria: 'Hortifruti' },
        { regex: /latic[ií]nio|queijo|leite|manteiga/i, categoria: 'Insumos', subcategoria: 'Laticínios' },
        { regex: /fruta|banana|laranja|lim[aã]o|abacaxi/i, categoria: 'Insumos', subcategoria: 'Frutas' },
        { regex: /gelo|gelada|freezer/i, categoria: 'Insumos', subcategoria: 'Gelo' },

        // Bebidas
        { regex: /cerveja|budweiser|heineken|stella|corona|brahma|skol/i, categoria: 'Bebidas', subcategoria: 'Cervejas' },
        { regex: /destilado|gin|vodka|whisky|rum|tequila|cacha[cç]a/i, categoria: 'Bebidas', subcategoria: 'Destilados' },
        { regex: /vinho|champagne|espumante/i, categoria: 'Bebidas', subcategoria: 'Vinhos' },
        { regex: /red\s*bull|monster|energ[eé]tico/i, categoria: 'Bebidas', subcategoria: 'Energético' },
        { regex: /bebida|refrigerante|[aá]gua|suco|coca/i, categoria: 'Bebidas', subcategoria: 'Bebidas' },

        // Operacional
        { regex: /embalagem|descart[aá]vel|guardanapo|sacola/i, categoria: 'Operacional', subcategoria: 'Embalagens' },
        { regex: /limpeza|higiene|detergente|desinfetante/i, categoria: 'Operacional', subcategoria: 'Limpeza' },
        { regex: /manuten[cç][aã]o|reparo|conserto|pe[cç]a/i, categoria: 'Operacional', subcategoria: 'Manutenção' },
        { regex: /g[aá]s|botij[aã]o|glp/i, categoria: 'Operacional', subcategoria: 'Gás' },

        // Pessoal
        { regex: /sal[aá]rio|folha|pagamento|holerite/i, categoria: 'Pessoal', subcategoria: 'Salário' },
        { regex: /pro\s*labore|prolabore|s[oó]cio/i, categoria: 'Pessoal', subcategoria: 'Pro Labore' },
        { regex: /freelancer|aut[oô]nomo|prestador|(?<!pag\s)\bfree\b/i, categoria: 'Pessoal', subcategoria: 'Freelancer' },
        { regex: /gorjeta|tip|gratifica[cç][aã]o/i, categoria: 'Pessoal', subcategoria: 'Gorjeta' },
        { regex: /venda\s*de\s*folga|folga\s*vendida/i, categoria: 'Pessoal', subcategoria: 'Venda de Folga' },
        { regex: /\bVT\b|vale\s*transporte/i, categoria: 'Pessoal', subcategoria: 'Vale Transporte' },
        { regex: /\bVR\b|vale\s*refei[cç][aã]o/i, categoria: 'Pessoal', subcategoria: 'Vale Refeição' },

        // Infraestrutura
        { regex: /aluguel|rent|loca[cç][aã]o/i, categoria: 'Infraestrutura', subcategoria: 'Aluguel' },
        { regex: /energia|luz|eletric|celesc|copel/i, categoria: 'Infraestrutura', subcategoria: 'Energia' },
        { regex: /seguro|seguradora|porto|mapfre/i, categoria: 'Infraestrutura', subcategoria: 'Seguros' },

        // Administrativo
        { regex: /imposto|taxa|darf|das|simples|icms|iss/i, categoria: 'Administrativo', subcategoria: 'Impostos' },
        { regex: /transporte|frete|uber|99|combustivel|gasolina/i, categoria: 'Administrativo', subcategoria: 'Transporte' },

        // Marketing e Eventos
        { regex: /evento|festa|show|confraterniza/i, categoria: 'Marketing e Eventos', subcategoria: 'Eventos' },
        { regex: /marketing|propaganda|anuncio|publicidade|instagram|facebook/i, categoria: 'Marketing e Eventos', subcategoria: 'Marketing' }
    ];

    /**
     * Detecta categoria e subcategoria baseado no nome do arquivo
     * @param {string} nomeArquivo - Nome do arquivo
     * @returns {Object|null} - {categoria, subcategoria} ou null se não encontrar
     */
    function detectarCategoriaPorNome(nomeArquivo) {
        if (!nomeArquivo) return null;

        const nomeNormalizado = nomeArquivo.toLowerCase();

        for (const mapa of MAPEAMENTO_NOMES_ARQUIVO) {
            if (mapa.regex.test(nomeNormalizado)) {
                return { categoria: mapa.categoria, subcategoria: mapa.subcategoria };
            }
        }

        return null;
    }

    /**
     * Atualiza as opções do select de subcategoria baseado na categoria selecionada
     * @param {string} categoria - Categoria selecionada
     * @param {string} subcategoriaPreSelecionada - Subcategoria a ser pré-selecionada (opcional)
     */
    function atualizarSubcategorias(categoria, subcategoriaPreSelecionada = null) {
        const selectSubcategoria = document.getElementById('subcategoria');
        if (!selectSubcategoria) return;

        const subcategorias = CATEGORIAS_SUBCATEGORIAS[categoria] || CATEGORIAS_SUBCATEGORIAS['Outros'];

        selectSubcategoria.innerHTML = subcategorias.map(sub =>
            `<option value="${sub.value}" ${sub.value === subcategoriaPreSelecionada ? 'selected' : ''}>${sub.label}</option>`
        ).join('');
    }

    // Event listener para mudança de categoria → atualiza subcategorias
    const selectCategoria = document.getElementById('categoria');
    if (selectCategoria) {
        selectCategoria.addEventListener('change', function () {
            atualizarSubcategorias(this.value);
        });
    }


    // =========================================
    // 1. Clique em Nova Despesa → Abre modal de escolha
    // =========================================
    btnNovaDespesa.addEventListener('click', function () {
        tipoAtual = 'DESPESA';
        document.getElementById('modal-escolha-titulo').textContent = 'Nova Despesa';
        document.getElementById('modal-escolha-header').className = 'modal-header bg-primary text-white';
        document.querySelector('#modal-escolha-label i').className = 'bi bi-receipt';
        escolhaModoModal.show();
    });

    // =========================================
    // 1b. Clique em Nova Receita → Abre modal de escolha
    // =========================================
    if (btnNovaReceita) {
        btnNovaReceita.addEventListener('click', function () {
            tipoAtual = 'RECEITA';
            document.getElementById('modal-escolha-titulo').textContent = 'Nova Receita';
            document.getElementById('modal-escolha-header').className = 'modal-header bg-success text-white';
            document.querySelector('#modal-escolha-label i').className = 'bi bi-cash-stack';
            escolhaModoModal.show();
        });
    }

    // =========================================
    // 1c. Escolha de modo: Único
    // =========================================
    btnModoUnico.addEventListener('click', function () {
        escolhaModoModal.hide();
        // Limpa input antes para garantir que change event dispare
        inputCamera.value = '';
        setTimeout(() => inputCamera.click(), 300);
    });

    // =========================================
    // 1d. Escolha de modo: Em Massa
    // =========================================
    btnModoMassa.addEventListener('click', function () {
        escolhaModoModal.hide();
        const inputMassaEl = document.getElementById('input-massa');
        // Limpa input antes para garantir que change event dispare
        inputMassaEl.value = '';
        setTimeout(() => inputMassaEl.click(), 300);
    });

    // =========================================
    // 2. Quando seleciona arquivo (imagem ou PDF)
    // =========================================
    inputCamera.addEventListener('change', async function (e) {
        const file = e.target.files[0];
        if (!file) return;

        // Detectar tipo de arquivo
        const isPDF = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
        const isImage = file.type.startsWith('image/');

        // Validar tipo de arquivo
        if (!isPDF && !isImage) {
            alert('Por favor, selecione uma imagem ou PDF válido.');
            return;
        }

        // Validar tamanho (máximo 16MB)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('Arquivo muito grande. Tamanho máximo: 16MB');
            return;
        }

        // Mostrar loading
        loadingModal.show();

        try {
            // Converter para base64
            const base64 = await fileToBase64(file);

            // Atualizar preview conforme tipo
            if (isPDF) {
                imgPreview.style.display = 'none';
                pdfPreview.classList.remove('d-none');
                pdfNome.textContent = file.name;
            } else {
                imgPreview.src = base64;
                imgPreview.style.display = 'block';
                pdfPreview.classList.add('d-none');
            }

            // Enviar para API (indicando se é PDF)
            const response = await fetch('/upload-nota', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    imagem: base64,
                    tipo_arquivo: isPDF ? 'pdf' : 'imagem',
                    nome_arquivo: file.name
                })
            });

            const result = await response.json();

            // Esconder loading
            loadingModal.hide();

            if (result.sucesso) {
                // Preencher formulário com dados da IA + nome do arquivo para detecção
                preencherFormulario(result.dados, result.comprovante_url, file.name);

                // Mostrar modal de conferência
                setTimeout(() => {
                    conferenciaModal.show();
                }, 300);
            } else {
                alert('Erro ao processar nota: ' + result.erro);
            }

        } catch (error) {
            loadingModal.hide();
            console.error('Erro:', error);
            alert('Erro ao processar arquivo. Verifique sua conexão e tente novamente.');
        }

        // Limpar input para permitir nova seleção
        inputCamera.value = '';
    });

    // =========================================
    // 3. Confirmar transação
    // =========================================
    btnConfirmar.addEventListener('click', async function () {
        // Validar formulário
        if (!formConferencia.checkValidity()) {
            formConferencia.reportValidity();
            return;
        }

        const formData = new FormData(formConferencia);
        const dados = Object.fromEntries(formData);

        // Converter valor para número
        dados.valor = parseFloat(dados.valor);

        if (isNaN(dados.valor) || dados.valor <= 0) {
            alert('Por favor, informe um valor válido.');
            return;
        }

        try {
            btnConfirmar.disabled = true;
            btnConfirmar.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Salvando...';

            const response = await fetch('/transacao', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });

            const result = await response.json();

            if (result.sucesso) {
                // Fechar modal de conferência
                conferenciaModal.hide();

                // Limpar formulário e preview
                formConferencia.reset();
                imgPreview.style.display = 'none';
                pdfPreview.classList.add('d-none');

                // Mostrar modal de sucesso
                setTimeout(() => {
                    sucessoModal.show();
                }, 300);
            } else {
                alert('Erro ao salvar: ' + result.erro);
            }

        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao salvar. Verifique sua conexão e tente novamente.');
        } finally {
            btnConfirmar.disabled = false;
            btnConfirmar.innerHTML = '<i class="bi bi-check-lg"></i> Confirmar';
        }
    });

    // =========================================
    // Funções auxiliares
    // =========================================

    /**
     * Converte arquivo para string Base64
     * @param {File} file - Arquivo a ser convertido
     * @returns {Promise<string>} - String Base64
     */
    function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Erro ao ler arquivo'));
            reader.readAsDataURL(file);
        });
    }

    /**
     * Preenche o formulário de conferência com dados da IA
     * @param {Object} dados - Dados extraídos da nota
     * @param {string} comprovanteUrl - URL do comprovante salvo
     * @param {string} nomeArquivo - Nome do arquivo para detecção automática
     */
    function preencherFormulario(dados, comprovanteUrl, nomeArquivo = null) {
        // Data
        if (dados.data) {
            document.getElementById('data').value = dados.data;
        } else {
            // Se não tiver data, usa a data atual
            document.getElementById('data').value = new Date().toISOString().split('T')[0];
        }

        // Estabelecimento
        if (dados.estabelecimento) {
            document.getElementById('estabelecimento').value = dados.estabelecimento;
        }

        // Valor
        if (dados.valor_total) {
            document.getElementById('valor').value = dados.valor_total.toFixed(2);
        }

        // Detectar categoria/subcategoria pelo nome do arquivo
        let categoriaDetectada = null;
        let subcategoriaDetectada = null;

        if (nomeArquivo) {
            const deteccao = detectarCategoriaPorNome(nomeArquivo);
            if (deteccao) {
                categoriaDetectada = deteccao.categoria;
                subcategoriaDetectada = deteccao.subcategoria;
                console.log(`📂 Detecção por nome: "${nomeArquivo}" → ${categoriaDetectada} / ${subcategoriaDetectada}`);
            }
        }

        // Categoria (prioriza detecção por nome, depois IA)
        const selectCategoriaEl = document.getElementById('categoria');
        if (selectCategoriaEl) {
            let categoriaFinal = categoriaDetectada || dados.categoria || 'Insumos';

            // Verifica se a categoria existe no select
            const opcaoCategoria = Array.from(selectCategoriaEl.options).find(
                opt => opt.value.toLowerCase() === categoriaFinal.toLowerCase()
            );

            if (opcaoCategoria) {
                selectCategoriaEl.value = opcaoCategoria.value;
            } else {
                selectCategoriaEl.value = 'Outros';
            }

            // Atualiza subcategorias baseado na categoria selecionada
            atualizarSubcategorias(selectCategoriaEl.value, subcategoriaDetectada);
        }

        // Descrição (observação baseada no nome do arquivo)
        if (dados.observacao) {
            document.getElementById('descricao').value = dados.observacao;
        } else if (nomeArquivo) {
            // Usa o nome do arquivo como descrição se não houver observação
            const nomeFormatado = nomeArquivo.replace(/\.[^.]+$/, '').replace(/[-_]/g, ' ');
            document.getElementById('descricao').value = nomeFormatado;
        }

        // URL do comprovante
        if (comprovanteUrl) {
            document.getElementById('comprovante-url').value = comprovanteUrl;
        }
    }

    // =========================================
    // UPLOAD EM MASSA
    // =========================================
    const inputMassa = document.getElementById('input-massa');
    const modalMassa = document.getElementById('modal-massa');
    const modalSucessoMassa = document.getElementById('modal-sucesso-massa');

    if (inputMassa && modalMassa) {
        const massaModal = new bootstrap.Modal(modalMassa);
        const sucessoMassaModal = new bootstrap.Modal(modalSucessoMassa);

        // Lista de categorias para despesas
        const CATEGORIAS_DESPESA = [
            { value: 'Frutos do Mar', label: '🦐 Frutos do Mar' },
            { value: 'Carnes e Aves', label: '🥩 Carnes e Aves' },
            { value: 'Hortifruti', label: '🥬 Hortifruti' },
            { value: 'Bebidas', label: '🥤 Bebidas' },
            { value: 'Cervejas', label: '🍺 Cervejas' },
            { value: 'Destilados', label: '🍸 Destilados' },
            { value: 'Vinhos', label: '🍾 Vinhos' },
            { value: 'Laticínios', label: '🧀 Laticínios' },
            { value: 'Embalagens', label: '📦 Embalagens' },
            { value: 'Limpeza', label: '🧹 Limpeza' },
            { value: 'Manutenção', label: '🔧 Manutenção' },
            { value: 'Gás', label: '🔥 Gás' },
            { value: 'Pessoal', label: '👥 Pessoal' },
            { value: 'Aluguel', label: '🏠 Aluguel' },
            { value: 'Energia', label: '💡 Energia' },
            { value: 'Seguros', label: '🛡️ Seguros' },
            { value: 'Organização', label: '📁 Organização' },
            { value: 'Frutas', label: '🍎 Frutas' },
            { value: 'Alimento (Variado)', label: '🥘 Alimento (Variado)' },
            { value: 'Eventos', label: '🎉 Eventos' },
            { value: 'Marketing', label: '📢 Marketing' },
            { value: 'Impostos', label: '🏛️ Impostos' },
            { value: 'Transporte', label: '🚚 Transporte' },
            { value: 'Outros', label: '📋 Outros' }
        ];

        // Lista de categorias para receitas
        const CATEGORIAS_RECEITA = [
            { value: 'PIX', label: '📱 PIX' },
            { value: 'Cartão', label: '💳 Cartão' },
            { value: 'Transferência', label: '🏦 Transferência' },
            { value: 'Vendas', label: '🛒 Vendas' },
            { value: 'Outros', label: '📋 Outros' }
        ];

        let resultadosMassa = [];

        // Quando seleciona múltiplos arquivos
        inputMassa.addEventListener('change', async function (e) {
            const files = Array.from(e.target.files);
            if (!files.length) return;

            // Valida quantidade
            if (files.length > 10) {
                alert('Máximo de 10 arquivos por vez. Você selecionou ' + files.length);
                inputMassa.value = '';
                return;
            }

            // Valida arquivos
            for (const file of files) {
                const isPDF = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
                const isImage = file.type.startsWith('image/');
                if (!isPDF && !isImage) {
                    alert(`Arquivo inválido: ${file.name}`);
                    inputMassa.value = '';
                    return;
                }
                if (file.size > 16 * 1024 * 1024) {
                    alert(`Arquivo muito grande: ${file.name}`);
                    inputMassa.value = '';
                    return;
                }
            }

            // Mostra modal com loading
            document.getElementById('massa-loading').classList.remove('d-none');
            document.getElementById('massa-lista').classList.add('d-none');
            document.getElementById('btn-confirmar-massa').classList.add('d-none');
            const progressoIni = document.getElementById('massa-progresso');
            if (progressoIni) progressoIni.textContent = `0/${files.length}`;
            massaModal.show();

            try {
                // Converte todos os arquivos para base64
                const arquivos = [];
                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    const base64 = await fileToBase64(file);
                    const isPDF = file.type === 'application/pdf';
                    arquivos.push({
                        imagem: base64,
                        nome_arquivo: file.name,
                        tipo_arquivo: isPDF ? 'pdf' : 'imagem'
                    });

                    const progressoEl = document.getElementById('massa-progresso');
                    if (progressoEl) {
                        progressoEl.textContent = `${i + 1}/${files.length}`;
                    }
                }

                // Envia para API
                const loadingTextEl = document.getElementById('massa-loading-text');
                if (loadingTextEl) {
                    loadingTextEl.textContent = 'Analisando com IA...';
                }

                const response = await fetch('/upload-notas-massa', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ arquivos })
                });

                const result = await response.json();

                if (result.sucesso) {
                    resultadosMassa = result.resultados;
                    renderizarListaMassa(resultadosMassa);
                } else {
                    alert('Erro: ' + result.erro);
                    massaModal.hide();
                }

            } catch (error) {
                console.error('Erro:', error);
                alert('Erro ao processar arquivos: ' + error.message);
                massaModal.hide();
            }

            inputMassa.value = '';
        });

        // Renderiza lista de itens para conferência
        function renderizarListaMassa(resultados) {
            document.getElementById('massa-loading').classList.add('d-none');
            document.getElementById('massa-lista').classList.remove('d-none');

            const container = document.getElementById('massa-itens');
            container.innerHTML = '';

            let totalSucesso = 0;

            resultados.forEach((item, index) => {
                if (!item.sucesso) {
                    // Item com erro
                    container.innerHTML += `
                        <div class="card mb-2 border-danger">
                            <div class="card-body p-2">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="text-danger"><i class="bi bi-x-circle"></i> ${item.nome_arquivo}</span>
                                    <small class="text-muted">${item.erro}</small>
                                </div>
                            </div>
                        </div>
                    `;
                    return;
                }

                totalSucesso++;
                const dados = item.dados;
                // Usa categorias baseado no tipo selecionado
                const categorias = tipoAtual === 'RECEITA' ? CATEGORIAS_RECEITA : CATEGORIAS_DESPESA;
                const categoriasOptions = categorias.map(c =>
                    `<option value="${c.value}" ${dados.categoria === c.value ? 'selected' : ''}>${c.label}</option>`
                ).join('');

                container.innerHTML += `
                    <div class="card mb-2 border-success item-massa" data-index="${index}">
                        <div class="card-body p-2">
                            <div class="row g-2 align-items-center">
                                <div class="col-12 col-md-2">
                                    <small class="text-muted d-block">${item.nome_arquivo}</small>
                                </div>
                                <div class="col-6 col-md-2">
                                    <input type="date" class="form-control form-control-sm" 
                                        name="data_${index}" value="${dados.data || new Date().toISOString().split('T')[0]}">
                                </div>
                                <div class="col-6 col-md-2">
                                    <input type="number" step="0.01" class="form-control form-control-sm" 
                                        name="valor_${index}" value="${dados.valor_total?.toFixed(2) || '0.00'}" placeholder="Valor">
                                </div>
                                <div class="col-12 col-md-3">
                                    <select class="form-select form-select-sm" name="categoria_${index}">
                                        ${categoriasOptions}
                                    </select>
                                </div>
                                <div class="col-12 col-md-3">
                                    <input type="text" class="form-control form-control-sm" 
                                        name="estabelecimento_${index}" value="${dados.estabelecimento || ''}" placeholder="Estabelecimento">
                                </div>
                            </div>
                            <input type="hidden" name="comprovante_${index}" value="${item.comprovante_url || ''}">
                            <input type="hidden" name="descricao_${index}" value="${dados.observacao || ''}">
                        </div>
                    </div>
                `;
            });

            // Mostra botão de confirmar
            if (totalSucesso > 0) {
                document.getElementById('btn-confirmar-massa').classList.remove('d-none');
                const massaTotalEl = document.getElementById('massa-total');
                if (massaTotalEl) {
                    massaTotalEl.textContent = totalSucesso;
                }
            }
        }

        // Confirmar todos
        document.getElementById('btn-confirmar-massa').addEventListener('click', async function () {
            const btn = this;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Salvando...';

            let salvos = 0;
            let erros = 0;

            for (let index = 0; index < resultadosMassa.length; index++) {
                const item = resultadosMassa[index];
                if (!item.sucesso) continue;

                const dados = {
                    tipo: tipoAtual,
                    data: document.querySelector(`[name="data_${index}"]`)?.value,
                    valor: parseFloat(document.querySelector(`[name="valor_${index}"]`)?.value || 0),
                    categoria: document.querySelector(`[name="categoria_${index}"]`)?.value,
                    estabelecimento: document.querySelector(`[name="estabelecimento_${index}"]`)?.value,
                    descricao: document.querySelector(`[name="descricao_${index}"]`)?.value,
                    comprovante_url: document.querySelector(`[name="comprovante_${index}"]`)?.value
                };

                try {
                    const response = await fetch('/transacao', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(dados)
                    });
                    const result = await response.json();
                    if (result.sucesso) salvos++;
                    else erros++;
                } catch (e) {
                    erros++;
                }
            }

            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-check-all"></i> Confirmar Todos (<span id="massa-total">0</span>)';

            // Reset do estado para permitir novo upload
            resetarModalMassa();

            massaModal.hide();

            const tipoTexto = tipoAtual === 'RECEITA' ? 'receita(s)' : 'despesa(s)';
            document.getElementById('massa-resultado-texto').textContent =
                `${salvos} ${tipoTexto} salva(s)${erros > 0 ? `, ${erros} erro(s)` : ''}`;

            setTimeout(() => sucessoMassaModal.show(), 300);
        });

        // Função para resetar o modal e permitir novo upload
        function resetarModalMassa() {
            resultadosMassa = [];
            document.getElementById('massa-itens').innerHTML = '';
            document.getElementById('massa-lista').classList.add('d-none');
            document.getElementById('massa-loading').classList.remove('d-none');
            document.getElementById('massa-loading-text').innerHTML = 'Processando arquivos... <span id="massa-progresso">0/0</span>';
            document.getElementById('btn-confirmar-massa').classList.add('d-none');
            inputMassa.value = '';
        }

        // Reset também quando o modal fecha (botão X ou Cancelar)
        modalMassa.addEventListener('hidden.bs.modal', function () {
            resetarModalMassa();
        });
    }
});
