# 📱 Fase 4: Frontend Mobile-First

> **Objetivo**: Implementar a interface do usuário com templates HTML responsivos, otimizados para uso no celular pelo gerente do restaurante.

---

## 🎭 ROLE

Você é um **Desenvolvedor Frontend Sênior** especializado em:
- Design responsivo e mobile-first
- HTML5 semântico e acessibilidade (a11y)
- CSS moderno (Flexbox, Grid, variáveis CSS)
- JavaScript assíncrono e manipulação de DOM

**Seu estilo de código:**
- Componentes reutilizáveis
- UX focado em performance e facilidade de uso
- Código JS modular sem dependências desnecessárias
- Estilos organizados e consistentes

---

## 📋 CONTEXTO

### Projeto
**GestorBot** é um sistema de gestão financeira para restaurantes com OCR inteligente de notas fiscais.

### O que já existe
```
MONA_Controle_financeiro/
├── config.py               # Configurações
├── models.py               # Modelo Transacao
├── app.py                  # Rotas Flask (GET /, POST /upload-nota, etc.)
├── requirements.txt        # Dependências
├── services/
│   ├── __init__.py
│   └── groq_service.py     # OCR com Groq
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Funções auxiliares
├── templates/              # ← IMPLEMENTAR AQUI
└── static/
    ├── css/                # ← IMPLEMENTAR AQUI
    ├── js/                 # ← IMPLEMENTAR AQUI
    └── uploads/
```

### Rotas Flask disponíveis
| Rota | Método | Template esperado |
|------|--------|-------------------|
| `/` | GET | `home.html` |
| `/dashboard` | GET | `dashboard.html` |
| `/receita` | GET | `receita.html` |
| `/upload-nota` | POST | (API JSON) |
| `/transacao` | POST | (API JSON) |

---

## 🎯 REQUISITOS TÉCNICOS

### 1. Criar `templates/base.html` - Template Base
**Critério de aceite**: Layout responsivo com navbar e container

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GestorBot{% endblock %}</title>
    
    <!-- Bootstrap 5 CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    
    <!-- CSS Customizado -->
    <link href="{{ url_for('static', filename='css/styles.css') }}" rel="stylesheet">
    
    {% block head %}{% endblock %}
</head>
<body>
    <!-- Navbar simples -->
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('home') }}">
                🍽️ GestorBot
            </a>
            <a href="{{ url_for('dashboard') }}" class="btn btn-outline-light btn-sm">
                <i class="bi bi-graph-up"></i> Dashboard
            </a>
        </div>
    </nav>
    
    <!-- Conteúdo principal -->
    <main class="container py-4">
        <!-- Flash messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- JS Customizado -->
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

---

### 2. Criar `templates/home.html` - Tela Inicial
**Critério de aceite**: Dois botões grandes e touch-friendly

```html
{% extends 'base.html' %}

{% block title %}GestorBot - Início{% endblock %}

{% block content %}
<div class="home-container">
    <h1 class="text-center mb-4">O que deseja fazer?</h1>
    
    <div class="d-grid gap-3">
        <!-- Botão Nova Despesa -->
        <button id="btn-nova-despesa" class="btn btn-primary btn-action">
            <i class="bi bi-camera-fill"></i>
            <span>Nova Despesa</span>
            <small>Tire foto da nota fiscal</small>
        </button>
        
        <!-- Botão Fechar Caixa -->
        <a href="{{ url_for('form_receita') }}" class="btn btn-success btn-action">
            <i class="bi bi-cash-stack"></i>
            <span>Fechar Caixa</span>
            <small>Lançar receita do dia</small>
        </a>
    </div>
    
    <!-- Input de câmera oculto -->
    <input type="file" id="input-camera" accept="image/*" capture="environment" class="d-none">
</div>

<!-- Modal de Loading -->
<div class="modal fade" id="modal-loading" data-bs-backdrop="static" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content text-center p-4">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Processando...</span>
            </div>
            <p class="mb-0">Analisando nota fiscal...</p>
            <small class="text-muted">Isso pode levar alguns segundos</small>
        </div>
    </div>
</div>

<!-- Modal de Conferência -->
<div class="modal fade" id="modal-conferencia" tabindex="-1">
    <div class="modal-dialog modal-fullscreen-sm-down">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Conferir Dados</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- Miniatura da imagem -->
                <div class="text-center mb-3">
                    <img id="img-preview" src="" alt="Nota" class="img-thumbnail" style="max-height: 150px;">
                </div>
                
                <!-- Formulário de conferência -->
                <form id="form-conferencia">
                    <input type="hidden" id="comprovante-url" name="comprovante_url">
                    <input type="hidden" name="tipo" value="DESPESA">
                    
                    <div class="mb-3">
                        <label for="data" class="form-label">Data</label>
                        <input type="date" class="form-control form-control-lg" id="data" name="data" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="estabelecimento" class="form-label">Estabelecimento</label>
                        <input type="text" class="form-control form-control-lg" id="estabelecimento" name="estabelecimento">
                    </div>
                    
                    <div class="mb-3">
                        <label for="valor" class="form-label">Valor Total (R$)</label>
                        <input type="number" step="0.01" class="form-control form-control-lg" id="valor" name="valor" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="categoria" class="form-label">Categoria</label>
                        <select class="form-select form-select-lg" id="categoria" name="categoria" required>
                            <option value="Hortifruti">🥬 Hortifruti</option>
                            <option value="Açougue">🥩 Açougue</option>
                            <option value="Bebidas">🍺 Bebidas</option>
                            <option value="Embalagens">📦 Embalagens</option>
                            <option value="Limpeza">🧹 Limpeza</option>
                            <option value="Manutenção">🔧 Manutenção</option>
                            <option value="Outros">📋 Outros</option>
                        </select>
                    </div>
                    
                    <div class="mb-3">
                        <label for="descricao" class="form-label">Descrição (opcional)</label>
                        <input type="text" class="form-control" id="descricao" name="descricao" placeholder="Ex: Compras semanais">
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" id="btn-confirmar" class="btn btn-primary btn-lg">
                    <i class="bi bi-check-lg"></i> Confirmar
                </button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
// Ver static/js/app.js para a lógica completa
</script>
{% endblock %}
```

---

### 3. Criar `templates/receita.html` - Formulário de Receita
**Critério de aceite**: Formulário simples para lançar fechamento de caixa

```html
{% extends 'base.html' %}

{% block title %}Lançar Receita{% endblock %}

{% block content %}
<div class="card">
    <div class="card-header bg-success text-white">
        <h5 class="mb-0"><i class="bi bi-cash-stack"></i> Fechar Caixa</h5>
    </div>
    <div class="card-body">
        <form id="form-receita" method="POST" action="{{ url_for('criar_transacao') }}">
            <input type="hidden" name="tipo" value="RECEITA">
            <input type="hidden" name="categoria" value="Vendas">
            
            <div class="mb-3">
                <label for="data" class="form-label">Data</label>
                <input type="date" class="form-control form-control-lg" id="data" name="data" 
                       value="{{ hoje }}" required>
            </div>
            
            <div class="mb-3">
                <label for="valor" class="form-label">Valor do Caixa (R$)</label>
                <input type="number" step="0.01" class="form-control form-control-lg" 
                       id="valor" name="valor" placeholder="0,00" required>
            </div>
            
            <div class="mb-3">
                <label for="descricao" class="form-label">Observação (opcional)</label>
                <input type="text" class="form-control" id="descricao" name="descricao" 
                       placeholder="Ex: Dia movimentado">
            </div>
            
            <div class="d-grid gap-2">
                <button type="submit" class="btn btn-success btn-lg">
                    <i class="bi bi-check-lg"></i> Registrar Receita
                </button>
                <a href="{{ url_for('home') }}" class="btn btn-outline-secondary">
                    <i class="bi bi-arrow-left"></i> Voltar
                </a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

---

### 4. Criar `templates/dashboard.html` - Painel Administrativo
**Critério de aceite**: Cards de métricas e gráfico de pizza

```html
{% extends 'base.html' %}

{% block title %}Dashboard - {{ mes_nome }} {{ ano }}{% endblock %}

{% block head %}
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
{% endblock %}

{% block content %}
<!-- Navegação de mês -->
<div class="d-flex justify-content-between align-items-center mb-4">
    <a href="{{ url_for('dashboard', mes=mes_anterior, ano=ano_anterior) }}" class="btn btn-outline-primary">
        <i class="bi bi-chevron-left"></i>
    </a>
    <h4 class="mb-0">{{ mes_nome }} {{ ano }}</h4>
    <a href="{{ url_for('dashboard', mes=mes_proximo, ano=ano_proximo) }}" class="btn btn-outline-primary">
        <i class="bi bi-chevron-right"></i>
    </a>
</div>

<!-- Cards de Métricas -->
<div class="row g-3 mb-4">
    <!-- Faturamento -->
    <div class="col-4">
        <div class="card text-center h-100 border-success">
            <div class="card-body p-2">
                <i class="bi bi-arrow-up-circle text-success fs-4"></i>
                <p class="text-muted small mb-1">Receita</p>
                <h5 class="text-success mb-0">R$ {{ "%.2f"|format(faturamento) }}</h5>
            </div>
        </div>
    </div>
    
    <!-- Despesas -->
    <div class="col-4">
        <div class="card text-center h-100 border-danger">
            <div class="card-body p-2">
                <i class="bi bi-arrow-down-circle text-danger fs-4"></i>
                <p class="text-muted small mb-1">Despesas</p>
                <h5 class="text-danger mb-0">R$ {{ "%.2f"|format(gastos) }}</h5>
            </div>
        </div>
    </div>
    
    <!-- Lucro -->
    <div class="col-4">
        <div class="card text-center h-100 border-primary">
            <div class="card-body p-2">
                <i class="bi bi-graph-up text-primary fs-4"></i>
                <p class="text-muted small mb-1">Lucro</p>
                <h5 class="{% if lucro >= 0 %}text-primary{% else %}text-danger{% endif %} mb-0">
                    R$ {{ "%.2f"|format(lucro) }}
                </h5>
            </div>
        </div>
    </div>
</div>

<!-- Gráfico de Pizza -->
<div class="card mb-4">
    <div class="card-header">
        <i class="bi bi-pie-chart"></i> Gastos por Categoria
    </div>
    <div class="card-body">
        {% if gastos_por_categoria %}
            <canvas id="grafico-categorias" style="max-height: 300px;"></canvas>
        {% else %}
            <p class="text-muted text-center py-4">Nenhuma despesa registrada neste mês.</p>
        {% endif %}
    </div>
</div>

<!-- Botão de Relatório -->
<div class="d-grid">
    <a href="{{ url_for('gerar_relatorio', mes=mes, ano=ano) }}" class="btn btn-outline-primary">
        <i class="bi bi-file-pdf"></i> Baixar Relatório PDF
    </a>
</div>
{% endblock %}

{% block scripts %}
{% if gastos_por_categoria %}
<script>
const ctx = document.getElementById('grafico-categorias').getContext('2d');
const dados = {{ gastos_por_categoria | tojson }};

const cores = {
    'Hortifruti': '#28a745',
    'Açougue': '#dc3545',
    'Bebidas': '#ffc107',
    'Embalagens': '#17a2b8',
    'Limpeza': '#6f42c1',
    'Manutenção': '#fd7e14',
    'Outros': '#6c757d'
};

new Chart(ctx, {
    type: 'pie',
    data: {
        labels: Object.keys(dados),
        datasets: [{
            data: Object.values(dados),
            backgroundColor: Object.keys(dados).map(cat => cores[cat] || '#6c757d')
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    }
});
</script>
{% endif %}
{% endblock %}
```

---

### 5. Criar `static/css/styles.css` - Estilos Customizados
**Critério de aceite**: Design mobile-first com botões grandes

```css
/* ========================================
   GestorBot - Estilos Mobile-First
   ======================================== */

/* Variáveis CSS */
:root {
    --primary-color: #0d6efd;
    --success-color: #198754;
    --danger-color: #dc3545;
    --spacing-lg: 1.5rem;
}

/* Reset / Base */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: #f8f9fa;
    min-height: 100vh;
}

/* Home Container */
.home-container {
    max-width: 400px;
    margin: 0 auto;
    padding-top: 2rem;
}

/* Botões de Ação (grandes, touch-friendly) */
.btn-action {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100px;
    padding: 1.5rem;
    font-size: 1.25rem;
    border-radius: 1rem;
    transition: transform 0.2s, box-shadow 0.2s;
}

.btn-action:active {
    transform: scale(0.98);
}

.btn-action i {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.btn-action small {
    font-size: 0.85rem;
    opacity: 0.8;
    font-weight: normal;
}

/* Cards de métricas */
.card {
    border-radius: 0.75rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* Formulários */
.form-control-lg,
.form-select-lg {
    font-size: 1.1rem;
    padding: 0.75rem 1rem;
}

/* Modal de conferência */
#modal-conferencia .modal-body {
    max-height: 70vh;
    overflow-y: auto;
}

/* Preview de imagem */
#img-preview {
    max-width: 100%;
    border-radius: 0.5rem;
}

/* Navbar */
.navbar-brand {
    font-weight: 600;
}

/* Responsivo: Desktop */
@media (min-width: 768px) {
    .home-container {
        padding-top: 4rem;
    }
    
    .btn-action {
        min-height: 120px;
    }
    
    .d-grid.gap-3 {
        display: grid !important;
        grid-template-columns: 1fr 1fr;
    }
}

/* Estados de Loading */
.loading {
    pointer-events: none;
    opacity: 0.7;
}

/* Animação de sucesso */
@keyframes success-pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.success-animation {
    animation: success-pulse 0.5s ease;
}
```

---

### 6. Criar `static/js/app.js` - Lógica JavaScript
**Critério de aceite**: Fluxo completo de upload → OCR → conferência → salvar

```javascript
/**
 * GestorBot - JavaScript Principal
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos
    const btnNovaDespesa = document.getElementById('btn-nova-despesa');
    const inputCamera = document.getElementById('input-camera');
    const modalLoading = document.getElementById('modal-loading');
    const modalConferencia = document.getElementById('modal-conferencia');
    const btnConfirmar = document.getElementById('btn-confirmar');
    const formConferencia = document.getElementById('form-conferencia');
    const imgPreview = document.getElementById('img-preview');
    
    // Se não estiver na home, não executar
    if (!btnNovaDespesa) return;
    
    // Bootstrap Modals
    const loadingModal = new bootstrap.Modal(modalLoading);
    const conferenciaModal = new bootstrap.Modal(modalConferencia);
    
    // 1. Clique no botão "Nova Despesa" → Abre câmera
    btnNovaDespesa.addEventListener('click', function() {
        inputCamera.click();
    });
    
    // 2. Quando seleciona/tira foto
    inputCamera.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        // Mostrar loading
        loadingModal.show();
        
        try {
            // Converter para base64
            const base64 = await fileToBase64(file);
            
            // Mostrar preview
            imgPreview.src = base64;
            
            // Enviar para API
            const response = await fetch('/upload-nota', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ imagem: base64 })
            });
            
            const result = await response.json();
            
            // Esconder loading
            loadingModal.hide();
            
            if (result.sucesso) {
                // Preencher formulário com dados da IA
                preencherFormulario(result.dados, result.comprovante_url);
                
                // Mostrar modal de conferência
                conferenciaModal.show();
            } else {
                alert('Erro: ' + result.erro);
            }
            
        } catch (error) {
            loadingModal.hide();
            console.error('Erro:', error);
            alert('Erro ao processar imagem. Tente novamente.');
        }
        
        // Limpar input para permitir nova seleção
        inputCamera.value = '';
    });
    
    // 3. Confirmar transação
    btnConfirmar.addEventListener('click', async function() {
        const formData = new FormData(formConferencia);
        const dados = Object.fromEntries(formData);
        
        // Converter valor para número
        dados.valor = parseFloat(dados.valor);
        
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
                conferenciaModal.hide();
                
                // Mostrar feedback de sucesso
                alert('✅ Despesa registrada com sucesso!');
                
                // Opcional: redirecionar para dashboard
                // window.location.href = '/dashboard';
            } else {
                alert('Erro: ' + result.erro);
            }
            
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao salvar. Tente novamente.');
        } finally {
            btnConfirmar.disabled = false;
            btnConfirmar.innerHTML = '<i class="bi bi-check-lg"></i> Confirmar';
        }
    });
    
    // Função auxiliar: File → Base64
    function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
    
    // Função auxiliar: Preencher formulário
    function preencherFormulario(dados, comprovanteUrl) {
        if (dados.data) {
            document.getElementById('data').value = dados.data;
        }
        if (dados.estabelecimento) {
            document.getElementById('estabelecimento').value = dados.estabelecimento;
        }
        if (dados.valor_total) {
            document.getElementById('valor').value = dados.valor_total.toFixed(2);
        }
        if (dados.categoria) {
            document.getElementById('categoria').value = dados.categoria;
        }
        if (comprovanteUrl) {
            document.getElementById('comprovante-url').value = comprovanteUrl;
        }
    }
});
```

---

## 📐 PADRÕES A SEGUIR

### HTML
- Sempre usar `form-control-lg` para inputs (facilita toque)
- Incluir atributos `aria-*` para acessibilidade
- IDs únicos e descritivos

### CSS
- Mobile-first: estilos base para mobile, `@media` para desktop
- Usar variáveis CSS para cores consistentes
- Botões com `min-height: 44px` (mínimo recomendado touch)

### JavaScript
- `async/await` para chamadas HTTP
- Tratamento de erros com try/catch
- Feedback visual durante operações

---

## 🚫 NÃO FAZER

1. ❌ **NÃO** usar jQuery - apenas JavaScript puro
2. ❌ **NÃO** criar animações pesadas - manter performance
3. ❌ **NÃO** usar tamanhos fixos em pixels para fontes
4. ❌ **NÃO** esquecer de limpar inputs após uso
5. ❌ **NÃO** deixar modais sem backdrop adequado
6. ❌ **NÃO** criar estilos inline - usar CSS externo
7. ❌ **NÃO** implementar dashboard com dados estáticos (usar dados do Flask)

---

## 📦 ENTREGÁVEIS

| # | Arquivo | Descrição |
|---|---------|-----------|
| 1 | `templates/base.html` | Template base com navbar e estrutura |
| 2 | `templates/home.html` | Tela inicial com botões de ação |
| 3 | `templates/receita.html` | Formulário de lançar receita |
| 4 | `templates/dashboard.html` | Painel com métricas e gráfico |
| 5 | `static/css/styles.css` | Estilos customizados |
| 6 | `static/js/app.js` | Lógica JavaScript |

---

## ✅ VERIFICAÇÃO

### 1. Iniciar servidor
```bash
cd MONA_Controle_financeiro
python app.py
```

### 2. Testar no navegador (mobile)
- Abrir http://localhost:5000 no celular (ou DevTools mobile)
- Verificar se botões são grandes o suficiente
- Clicar em "Nova Despesa" → Deve abrir câmera

### 3. Testar fluxo completo
1. Tirar foto de uma nota fiscal
2. Aguardar loading
3. Verificar se dados foram preenchidos
4. Editar se necessário
5. Confirmar
6. Verificar mensagem de sucesso

### 4. Testar Dashboard
- Acessar http://localhost:5000/dashboard
- Verificar se cards aparecem
- Verificar se gráfico renderiza (se houver dados)
- Navegar entre meses

### 5. Responsividade
- Testar em telas de 320px (mínimo)
- Testar em tablet (768px)
- Testar em desktop (1024px+)

---

## 📝 NOTAS ADICIONAIS

### Sobre capture="environment"
```html
<input type="file" accept="image/*" capture="environment">
```
- `capture="environment"` = câmera traseira (para fotos de notas)
- `capture="user"` = câmera frontal (selfies)

### Meses para dashboard
O Flask precisa passar estas variáveis para o template:
```python
# No controller dashboard():
meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
```

### Cores das categorias (Chart.js)
Manter consistência com os emojis/cores do select:
- 🥬 Hortifruti → Verde (#28a745)
- 🥩 Açougue → Vermelho (#dc3545)
- 🍺 Bebidas → Amarelo (#ffc107)
- etc.

---

> **Próxima fase**: Fase 5 - Dashboard Administrativo (refinamentos)
