# 📊 Fase 5: Dashboard Administrativo (Refinamentos)

> **Objetivo**: Aprimorar o dashboard com visualizações avançadas, navegação entre períodos e métricas detalhadas para o proprietário do restaurante.

---

## 🎭 ROLE

Você é um **Desenvolvedor Full-Stack Sênior** especializado em:
- Visualização de dados e dashboards interativos
- Integração Flask + Jinja2 + Chart.js
- UX para exibição de métricas financeiras
- Performance e otimização de queries

**Seu estilo de código:**
- Dados pré-processados no backend, não no frontend
- Gráficos responsivos e acessíveis
- Formatação de moeda brasileira (R$)
- Código limpo e reutilizável

---

## 📋 CONTEXTO

### Projeto
**GestorBot** é um sistema de gestão financeira para restaurantes com OCR inteligente de notas fiscais.

### O que já existe
```
MONA_Controle_financeiro/
├── config.py               # Configurações
├── models.py               # Transacao + funções auxiliares
├── app.py                  # Rotas Flask (incluindo /dashboard)
├── services/
│   └── groq_service.py     # OCR com Groq
├── templates/
│   ├── base.html           # Template base
│   ├── home.html           # Tela inicial
│   ├── receita.html        # Formulário de receita
│   └── dashboard.html      # ← APRIMORAR AQUI
└── static/
    ├── css/styles.css      # Estilos
    └── js/app.js           # JavaScript
```

### Funções disponíveis (models.py)
```python
from models import get_transacoes_mes, get_totais_mes, get_gastos_por_categoria

# Retorna lista de transações do mês
transacoes = get_transacoes_mes(ano=2025, mes=12)

# Retorna {receitas: float, despesas: float, lucro: float}
totais = get_totais_mes(ano=2025, mes=12)

# Retorna {categoria: valor, ...}
gastos = get_gastos_por_categoria(ano=2025, mes=12)
```

---

## 🎯 REQUISITOS TÉCNICOS

### 1. Atualizar rota `/dashboard` em `app.py`
**Critério de aceite**: Passar todos os dados necessários para o template

```python
@app.route('/dashboard')
def dashboard():
    """
    Renderiza dashboard com métricas financeiras.
    
    Query Parameters:
        - mes: int (1-12, default: mês atual)
        - ano: int (default: ano atual)
    
    Contexto passado ao template:
        - faturamento: float
        - gastos: float
        - lucro: float
        - gastos_por_categoria: dict
        - transacoes_recentes: list (últimas 10)
        - mes: int
        - ano: int
        - mes_nome: str
        - mes_anterior: int
        - ano_anterior: int
        - mes_proximo: int
        - ano_proximo: int
    """
    # Obter mês/ano dos query params ou usar atual
    hoje = date.today()
    mes = request.args.get('mes', hoje.month, type=int)
    ano = request.args.get('ano', hoje.year, type=int)
    
    # Validar mês
    if mes < 1 or mes > 12:
        mes = hoje.month
    
    # Calcular mês anterior e próximo
    # ...implementar lógica de navegação...
    
    # Buscar dados
    totais = get_totais_mes(ano, mes)
    gastos_cat = get_gastos_por_categoria(ano, mes)
    transacoes = get_transacoes_mes(ano, mes)
    
    # Ordenar transações por data (mais recentes primeiro)
    transacoes_recentes = sorted(transacoes, key=lambda t: t.data, reverse=True)[:10]
    
    # Nomes dos meses em português
    meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    return render_template('dashboard.html',
        faturamento=totais['receitas'],
        gastos=totais['despesas'],
        lucro=totais['lucro'],
        gastos_por_categoria=gastos_cat,
        transacoes_recentes=[t.to_dict() for t in transacoes_recentes],
        mes=mes,
        ano=ano,
        mes_nome=meses_nomes[mes],
        # ... navegação ...
    )
```

---

### 2. Aprimorar `templates/dashboard.html`
**Critério de aceite**: Dashboard completo com todas as seções

#### Seção 1: Header com Navegação de Período
```html
<div class="d-flex justify-content-between align-items-center mb-4">
    <a href="?mes={{ mes_anterior }}&ano={{ ano_anterior }}" class="btn btn-outline-primary">
        <i class="bi bi-chevron-left"></i>
    </a>
    <h4 class="mb-0">{{ mes_nome }} {{ ano }}</h4>
    <a href="?mes={{ mes_proximo }}&ano={{ ano_proximo }}" class="btn btn-outline-primary">
        <i class="bi bi-chevron-right"></i>
    </a>
</div>
```

#### Seção 2: Cards de Métricas (com animação)
```html
<div class="row g-3 mb-4">
    <!-- Card Receita -->
    <div class="col-4">
        <div class="card metric-card text-center h-100 border-success">
            <div class="card-body p-2">
                <i class="bi bi-arrow-up-circle-fill text-success fs-3"></i>
                <p class="text-muted small mb-1">Receita</p>
                <h5 class="text-success mb-0" data-value="{{ faturamento }}">
                    R$ {{ "%.2f"|format(faturamento) }}
                </h5>
            </div>
        </div>
    </div>
    
    <!-- Card Despesas -->
    <div class="col-4">
        <div class="card metric-card text-center h-100 border-danger">
            <div class="card-body p-2">
                <i class="bi bi-arrow-down-circle-fill text-danger fs-3"></i>
                <p class="text-muted small mb-1">Despesas</p>
                <h5 class="text-danger mb-0">
                    R$ {{ "%.2f"|format(gastos) }}
                </h5>
            </div>
        </div>
    </div>
    
    <!-- Card Lucro -->
    <div class="col-4">
        <div class="card metric-card text-center h-100 
             {% if lucro >= 0 %}border-primary{% else %}border-warning{% endif %}">
            <div class="card-body p-2">
                <i class="bi bi-graph-up-arrow 
                   {% if lucro >= 0 %}text-primary{% else %}text-warning{% endif %} fs-3"></i>
                <p class="text-muted small mb-1">Lucro</p>
                <h5 class="{% if lucro >= 0 %}text-primary{% else %}text-warning{% endif %} mb-0">
                    R$ {{ "%.2f"|format(lucro) }}
                </h5>
            </div>
        </div>
    </div>
</div>
```

#### Seção 3: Gráfico de Pizza (Gastos por Categoria)
```html
<div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
        <span><i class="bi bi-pie-chart-fill"></i> Gastos por Categoria</span>
        <span class="badge bg-secondary">{{ gastos_por_categoria|length }} categorias</span>
    </div>
    <div class="card-body">
        {% if gastos_por_categoria %}
            <div class="row">
                <div class="col-md-6">
                    <canvas id="grafico-categorias" style="max-height: 250px;"></canvas>
                </div>
                <div class="col-md-6">
                    <ul class="list-group list-group-flush">
                        {% for categoria, valor in gastos_por_categoria.items() %}
                        <li class="list-group-item d-flex justify-content-between">
                            <span>{{ categoria }}</span>
                            <strong>R$ {{ "%.2f"|format(valor) }}</strong>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        {% else %}
            <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox fs-1"></i>
                <p>Nenhuma despesa registrada neste mês.</p>
            </div>
        {% endif %}
    </div>
</div>
```

#### Seção 4: Transações Recentes
```html
<div class="card mb-4">
    <div class="card-header">
        <i class="bi bi-clock-history"></i> Últimas Transações
    </div>
    <div class="card-body p-0">
        {% if transacoes_recentes %}
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead class="table-light">
                        <tr>
                            <th>Data</th>
                            <th>Descrição</th>
                            <th>Categoria</th>
                            <th class="text-end">Valor</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for t in transacoes_recentes %}
                        <tr>
                            <td>{{ t.data_formatada }}</td>
                            <td>{{ t.descricao or t.estabelecimento or '-' }}</td>
                            <td><span class="badge bg-secondary">{{ t.categoria }}</span></td>
                            <td class="text-end {% if t.tipo == 'RECEITA' %}text-success{% else %}text-danger{% endif %}">
                                {% if t.tipo == 'RECEITA' %}+{% else %}-{% endif %}
                                R$ {{ "%.2f"|format(t.valor) }}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <div class="text-center py-4 text-muted">
                Nenhuma transação neste período.
            </div>
        {% endif %}
    </div>
</div>
```

#### Seção 5: Botão de Relatório
```html
<div class="d-grid gap-2">
    <a href="{{ url_for('gerar_relatorio', mes=mes, ano=ano) }}" 
       class="btn btn-outline-primary btn-lg">
        <i class="bi bi-file-earmark-pdf"></i> Baixar Relatório PDF
    </a>
    <a href="{{ url_for('home') }}" class="btn btn-outline-secondary">
        <i class="bi bi-house"></i> Voltar ao Início
    </a>
</div>
```

---

### 3. Adicionar estilos em `static/css/styles.css`
**Critério de aceite**: Cards com visual premium e transições suaves

```css
/* Dashboard - Cards de Métricas */
.metric-card {
    transition: transform 0.2s, box-shadow 0.2s;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.metric-card h5 {
    font-size: 1.1rem;
    font-weight: 700;
}

/* Responsivo: ajustar fonte em telas pequenas */
@media (max-width: 576px) {
    .metric-card h5 {
        font-size: 0.9rem;
    }
    .metric-card .fs-3 {
        font-size: 1.25rem !important;
    }
}

/* Tabela de transações */
.table-hover tbody tr:hover {
    background-color: rgba(13, 110, 253, 0.05);
}

/* Badge de categoria com cores */
.badge-Hortifruti { background-color: #28a745 !important; }
.badge-Açougue { background-color: #dc3545 !important; }
.badge-Bebidas { background-color: #ffc107 !important; color: #000; }
.badge-Embalagens { background-color: #17a2b8 !important; }
.badge-Limpeza { background-color: #6f42c1 !important; }
.badge-Manutenção { background-color: #fd7e14 !important; }
.badge-Outros { background-color: #6c757d !important; }
```

---

### 4. Configurar Chart.js no template
**Critério de aceite**: Gráfico de pizza funcional e responsivo

```javascript
{% if gastos_por_categoria %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('grafico-categorias').getContext('2d');
    const dados = {{ gastos_por_categoria | tojson }};
    
    // Cores por categoria
    const coresCategorias = {
        'Hortifruti': '#28a745',
        'Açougue': '#dc3545',
        'Bebidas': '#ffc107',
        'Embalagens': '#17a2b8',
        'Limpeza': '#6f42c1',
        'Manutenção': '#fd7e14',
        'Outros': '#6c757d',
        'Vendas': '#198754'
    };
    
    const labels = Object.keys(dados);
    const valores = Object.values(dados);
    const cores = labels.map(cat => coresCategorias[cat] || '#6c757d');
    
    new Chart(ctx, {
        type: 'doughnut',  // ou 'pie'
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
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `R$ ${value.toFixed(2)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
});
</script>
{% endif %}
```

---

## 📐 PADRÕES A SEGUIR

### Formatação de Moeda
```python
# No Jinja2
{{ "%.2f"|format(valor) }}  # 1234.56

# Ou criar filtro customizado
@app.template_filter('moeda')
def filtro_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
```

### Cálculo de Navegação entre Meses
```python
# Mês anterior
if mes == 1:
    mes_anterior, ano_anterior = 12, ano - 1
else:
    mes_anterior, ano_anterior = mes - 1, ano

# Próximo mês
if mes == 12:
    mes_proximo, ano_proximo = 1, ano + 1
else:
    mes_proximo, ano_proximo = mes + 1, ano
```

---

## 🚫 NÃO FAZER

1. ❌ **NÃO** fazer cálculos complexos no JavaScript - calcular no Python
2. ❌ **NÃO** expor todos os dados das transações - apenas o necessário
3. ❌ **NÃO** criar múltiplas chamadas ao banco - usar funções existentes
4. ❌ **NÃO** hardcodar cores fora do padrão estabelecido
5. ❌ **NÃO** deixar o gráfico quebrar em telas pequenas
6. ❌ **NÃO** mostrar dados de meses futuros

---

## 📦 ENTREGÁVEIS

| # | Arquivo | Descrição |
|---|---------|-----------|
| 1 | `app.py` | Rota `/dashboard` atualizada com todos os dados |
| 2 | `templates/dashboard.html` | Template completo com todas as seções |
| 3 | `static/css/styles.css` | Estilos adicionais para dashboard |

---

## ✅ VERIFICAÇÃO

### 1. Verificar rota com dados
```bash
# Criar algumas transações de teste primeiro
curl -X POST http://localhost:5000/transacao \
  -H "Content-Type: application/json" \
  -d '{"tipo":"DESPESA","valor":150,"data":"2025-12-20","categoria":"Hortifruti","descricao":"CEASA"}'

curl -X POST http://localhost:5000/transacao \
  -H "Content-Type: application/json" \
  -d '{"tipo":"RECEITA","valor":500,"data":"2025-12-20","categoria":"Vendas","descricao":"Fechamento"}'
```

### 2. Acessar dashboard
- Abrir http://localhost:5000/dashboard
- Verificar se cards mostram valores corretos
- Verificar se gráfico renderiza
- Verificar se tabela mostra transações

### 3. Testar navegação
- Clicar em "◀" → Deve ir para Novembro
- Clicar em "▶" → Deve voltar para Dezembro
- Verificar se URL muda (?mes=11&ano=2025)

### 4. Testar responsividade
- Redimensionar para mobile (375px)
- Verificar se cards se ajustam
- Verificar se tabela tem scroll horizontal
- Verificar se gráfico redimensiona

---

## 📝 NOTAS ADICIONAIS

### Sobre performance
- As funções `get_totais_mes()` e `get_gastos_por_categoria()` já filtram no banco
- Evitar carregar todas as transações se não for necessário

### Sobre o gráfico doughnut vs pie
- `doughnut` é mais moderno e deixa espaço para uma métrica central
- `pie` é mais tradicional
- Usar `doughnut` por padrão

### Cores consistentes
Manter as mesmas cores em:
- Gráfico Chart.js
- Badges da tabela
- Select de categorias (Fase 4)

---

> **Próxima fase**: Fase 6 - Relatório Automático PDF
