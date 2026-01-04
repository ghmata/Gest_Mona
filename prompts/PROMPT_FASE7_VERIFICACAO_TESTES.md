# ✅ Fase 7: Verificação e Testes Finais

> **Objetivo**: Validar o funcionamento completo do sistema através de testes manuais, correção de bugs e polimento final antes da entrega.

---

## 🎭 ROLE

Você é um **QA Engineer / Desenvolvedor Sênior** especializado em:
- Testes de integração e end-to-end
- Debugging e resolução de problemas
- Validação de fluxos de usuário
- Documentação de sistemas

**Seu estilo de trabalho:**
- Testes sistemáticos e documentados
- Identificação precisa de bugs
- Correções cirúrgicas sem introduzir novos problemas
- Foco na experiência do usuário final

---

## 📋 CONTEXTO

### Projeto
**GestorBot** é um sistema de gestão financeira para restaurantes com OCR inteligente de notas fiscais.

### O que já existe (projeto completo)
```
MONA_Controle_financeiro/
├── config.py               # ✅ Configurações
├── models.py               # ✅ Modelo Transacao
├── app.py                  # ✅ Rotas Flask
├── requirements.txt        # ✅ Dependências
├── .env.example            # ✅ Template de variáveis
├── .gitignore              # ✅ Arquivos ignorados
├── services/
│   ├── __init__.py
│   ├── groq_service.py     # ✅ OCR com Groq
│   └── pdf_service.py      # ✅ Geração de PDF
├── utils/
│   ├── __init__.py
│   └── helpers.py          # ✅ Funções auxiliares
├── templates/
│   ├── base.html           # ✅ Template base
│   ├── home.html           # ✅ Tela inicial
│   ├── receita.html        # ✅ Formulário receita
│   └── dashboard.html      # ✅ Dashboard
└── static/
    ├── css/styles.css      # ✅ Estilos
    ├── js/app.js           # ✅ JavaScript
    └── uploads/            # ✅ Pasta de uploads
```

---

## 🎯 REQUISITOS DE VERIFICAÇÃO

### 1. Checklist de Ambiente

#### 1.1. Verificar estrutura de pastas
```bash
cd MONA_Controle_financeiro

# Verificar arquivos principais
dir *.py
# Esperado: config.py, models.py, app.py

# Verificar serviços
dir services\*.py
# Esperado: __init__.py, groq_service.py, pdf_service.py

# Verificar templates
dir templates\*.html
# Esperado: base.html, home.html, receita.html, dashboard.html

# Verificar estáticos
dir static\css\*.css
dir static\js\*.js
```

#### 1.2. Verificar dependências
```bash
# Criar ambiente virtual (se não existir)
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list | findstr flask
pip list | findstr groq
pip list | findstr fpdf
```

#### 1.3. Configurar variáveis de ambiente
```bash
# Copiar template
copy .env.example .env

# Editar .env e adicionar GROQ_API_KEY real
# Obter chave em: https://console.groq.com/
```

---

### 2. Testes de Backend

#### 2.1. Inicialização do servidor
```bash
python app.py
```
**Resultado esperado:**
```
INFO:__main__:✅ Banco de dados inicializado
INFO:__main__:🚀 GestorBot iniciando em http://0.0.0.0:5000
```

#### 2.2. Teste de rota home
```bash
curl http://localhost:5000/
```
**Resultado esperado:** HTML da página home (sem erros 500)

#### 2.3. Teste de criação de transação (DESPESA)
```bash
curl -X POST http://localhost:5000/transacao ^
  -H "Content-Type: application/json" ^
  -d "{\"tipo\":\"DESPESA\",\"valor\":150.50,\"data\":\"2025-12-26\",\"categoria\":\"Hortifruti\",\"descricao\":\"Compras CEASA\"}"
```
**Resultado esperado:**
```json
{"sucesso": true, "id": 1, "mensagem": "Transação registrada com sucesso!"}
```

#### 2.4. Teste de criação de transação (RECEITA)
```bash
curl -X POST http://localhost:5000/transacao ^
  -H "Content-Type: application/json" ^
  -d "{\"tipo\":\"RECEITA\",\"valor\":500.00,\"data\":\"2025-12-26\",\"categoria\":\"Vendas\",\"descricao\":\"Fechamento do dia\"}"
```

#### 2.5. Teste de listagem de transações
```bash
curl http://localhost:5000/transacoes
```
**Resultado esperado:**
```json
{"transacoes": [...], "total": 2, "filtros": {...}}
```

#### 2.6. Teste de validação de entrada
```bash
# Valor negativo (deve falhar)
curl -X POST http://localhost:5000/transacao ^
  -H "Content-Type: application/json" ^
  -d "{\"tipo\":\"DESPESA\",\"valor\":-100,\"data\":\"2025-12-26\",\"categoria\":\"Outros\"}"
```
**Resultado esperado:**
```json
{"sucesso": false, "erro": "Valor deve ser positivo"}
```

---

### 3. Testes de Frontend

#### 3.1. Tela Home (Mobile)
- [ ] Abrir http://localhost:5000 no celular (ou DevTools mobile 375x667)
- [ ] Verificar se botões "Nova Despesa" e "Fechar Caixa" são grandes
- [ ] Verificar se botão "Dashboard" está visível
- [ ] Clicar em "Nova Despesa" → Deve abrir câmera/seletor de arquivo

#### 3.2. Fluxo de Nova Despesa
- [ ] Tirar/selecionar foto de uma nota fiscal
- [ ] Verificar se modal de loading aparece
- [ ] Verificar se dados são preenchidos automaticamente
- [ ] Editar um campo manualmente
- [ ] Clicar em "Confirmar"
- [ ] Verificar mensagem de sucesso

#### 3.3. Fluxo de Receita
- [ ] Clicar em "Fechar Caixa"
- [ ] Preencher valor e data
- [ ] Clicar em "Registrar Receita"
- [ ] Verificar redirecionamento para home

#### 3.4. Dashboard
- [ ] Acessar http://localhost:5000/dashboard
- [ ] Verificar se cards de métricas mostram valores corretos
- [ ] Verificar se gráfico de pizza renderiza
- [ ] Navegar para mês anterior (◀)
- [ ] Navegar para próximo mês (▶)
- [ ] Verificar lista de transações recentes

#### 3.5. Relatório PDF
- [ ] Clicar em "Baixar Relatório PDF"
- [ ] Verificar se download inicia
- [ ] Abrir PDF e verificar conteúdo

---

### 4. Testes de OCR (Groq)

#### 4.1. Foto legível
- [ ] Usar nota fiscal clara, bem iluminada
- [ ] Verificar se data é extraída corretamente
- [ ] Verificar se valor é extraído corretamente
- [ ] Verificar se categoria é classificada razoavelmente

#### 4.2. Foto ilegível
- [ ] Usar foto escura ou borrada
- [ ] Verificar se sistema retorna erro amigável
- [ ] Verificar se permite tentar novamente

#### 4.3. Imagem não-nota
- [ ] Usar foto de paisagem ou objeto qualquer
- [ ] Verificar se sistema identifica que não é nota fiscal

---

### 5. Testes de Responsividade

| Dispositivo | Largura | Verificar |
|-------------|---------|-----------|
| iPhone SE | 375px | Botões, cards, gráfico |
| iPhone 12 | 390px | Botões, cards, gráfico |
| iPad | 768px | Layout 2 colunas |
| Desktop | 1024px+ | Layout completo |

---

### 6. Bugs Comuns e Correções

#### Bug 1: Modal não fecha após sucesso
```javascript
// Em static/js/app.js
// Verificar se está chamando:
conferenciaModal.hide();
```

#### Bug 2: Data em formato errado
```python
# Em models.py - verificar format
self.data.strftime('%Y-%m-%d')  # Para API
self.data.strftime('%d/%m/%Y')  # Para exibição
```

#### Bug 3: Gráfico não renderiza
```html
<!-- Em dashboard.html - verificar se Chart.js está carregado -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

#### Bug 4: PDF com caracteres estranhos
```python
# Em pdf_service.py - FPDF2 suporta UTF-8 nativamente
# Verificar se não está usando encode/decode desnecessário
```

#### Bug 5: Imagem não salva
```python
# Em app.py - verificar se pasta existe
import os
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
```

---

### 7. Criar README.md

**Critério de aceite**: Documentação completa para o usuário final

```markdown
# 🍽️ GestorBot - Gestão Financeira para Restaurantes

Sistema inteligente para controle de despesas e receitas com OCR de notas fiscais.

## 🚀 Funcionalidades

- 📷 **OCR Inteligente**: Tire foto da nota fiscal e o sistema preenche automaticamente
- 💰 **Controle de Caixa**: Lance receitas com um clique
- 📊 **Dashboard**: Visualize métricas e gráficos em tempo real
- 📄 **Relatórios PDF**: Gere relatórios mensais automaticamente

## 📋 Pré-requisitos

- Python 3.11+
- Conta na Groq (para OCR): https://console.groq.com/

## 🔧 Instalação

1. Clone ou copie o projeto
2. Crie ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
3. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure variáveis de ambiente:
   ```bash
   copy .env.example .env
   # Edite .env e adicione sua GROQ_API_KEY
   ```

## ▶️ Executando

```bash
python app.py
```

Acesse: http://localhost:5000

## 📱 Uso

1. **Nova Despesa**: Tire foto da nota fiscal → Confira dados → Confirme
2. **Fechar Caixa**: Informe valor do dia → Registre
3. **Dashboard**: Acompanhe métricas e gere relatórios

## 📁 Estrutura

```
├── app.py              # Aplicação principal
├── models.py           # Modelos de dados
├── config.py           # Configurações
├── services/           # Serviços (Groq, PDF)
├── templates/          # Páginas HTML
└── static/             # CSS, JS, uploads
```

## 🆘 Suporte

Em caso de problemas, verifique:
1. Se a GROQ_API_KEY está configurada corretamente
2. Se todas as dependências foram instaladas
3. Se está usando Python 3.11+
```

---

## 📐 PADRÕES A SEGUIR

### Documentação de Bugs
```markdown
## Bug #X: [Descrição curta]
- **Onde**: Arquivo e função
- **Sintoma**: O que acontece
- **Causa**: Por que acontece
- **Correção**: O que foi feito
```

### Commits de Correção
```
fix: corrigir modal não fechando após sucesso
fix: ajustar formato de data no dashboard
fix: corrigir encoding do PDF
```

---

## 🚫 NÃO FAZER

1. ❌ **NÃO** modificar funcionalidades que estão funcionando
2. ❌ **NÃO** adicionar features novas nesta fase
3. ❌ **NÃO** ignorar erros no console
4. ❌ **NÃO** pular testes de responsividade
5. ❌ **NÃO** entregar sem testar no mobile real
6. ❌ **NÃO** deixar console.log ou print de debug

---

## 📦 ENTREGÁVEIS

| # | Arquivo | Descrição |
|---|---------|-----------|
| 1 | `README.md` | Documentação do projeto |
| 2 | Correções de bugs | Arquivos modificados conforme necessário |
| 3 | Checklist de testes | Documento com todos os testes realizados |

---

## ✅ CHECKLIST FINAL

### Ambiente
- [ ] Servidor inicia sem erros
- [ ] Banco de dados é criado automaticamente
- [ ] Variáveis de ambiente funcionam

### Backend
- [ ] Criar transação DESPESA funciona
- [ ] Criar transação RECEITA funciona
- [ ] Listar transações funciona
- [ ] Dashboard calcula métricas corretamente
- [ ] Relatório PDF é gerado

### Frontend
- [ ] Home carrega em mobile
- [ ] Botões são touch-friendly
- [ ] Modal de conferência funciona
- [ ] Dashboard exibe gráfico
- [ ] Navegação entre meses funciona

### OCR
- [ ] Foto legível extrai dados
- [ ] Foto ilegível mostra erro amigável
- [ ] API key inválida mostra erro amigável

### Geral
- [ ] Nenhum erro no console do navegador
- [ ] Nenhum erro no terminal do servidor
- [ ] README.md está completo
- [ ] .env.example está atualizado

---

## 📝 NOTAS FINAIS

### Após aprovação nos testes
1. Remover dados de teste do banco (ou recriar banco limpo)
2. Verificar se .env não está no git
3. Fazer backup do projeto
4. Entregar ao cliente com instruções

### Próximos passos (pós-MVP)
- Autenticação de usuários
- Suporte a múltiplos restaurantes
- Backup automático do banco
- App mobile nativo (PWA)

---

> 🎉 **Parabéns!** Se todos os testes passaram, o GestorBot está pronto para uso!
