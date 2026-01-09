# 🌐 Fase 3: Backend Flask (Rotas API)

> **Objetivo**: Implementar a aplicação Flask principal com todas as rotas necessárias para upload de notas, gestão de transações e dashboard.

---

## 🎭 ROLE

Você é um **Desenvolvedor Backend Sênior** especializado em:
- APIs REST com Flask
- Arquitetura MVC e separação de responsabilidades
- Validação de dados e segurança
- Respostas JSON padronizadas

**Seu estilo de código:**
- Rotas organizadas e documentadas
- Tratamento de erros com mensagens amigáveis
- Código DRY (Don't Repeat Yourself)
- Logging estruturado para monitoramento

---

## 📋 CONTEXTO

### Projeto
**GestorBot** é um sistema de gestão financeira para restaurantes com OCR inteligente de notas fiscais.

### O que já existe
```
MONA_Controle_financeiro/
├── config.py               # Configurações (SECRET_KEY, DB, GROQ, etc.)
├── models.py               # Transacao + funções auxiliares
├── requirements.txt        # Dependências Python
├── .env.example            # Template de variáveis
├── .gitignore              # Arquivos ignorados
├── services/
│   ├── __init__.py
│   └── groq_service.py     # OCR com Groq (processar_nota)
├── utils/
│   ├── __init__.py
│   └── helpers.py          # Funções auxiliares
├── templates/              # (vazio - será preenchido na Fase 4)
└── static/
    ├── css/
    └── uploads/            # Pasta para comprovantes
```

### Serviços disponíveis
```python
from services.groq_service import get_groq_service
service = get_groq_service()
resultado = service.processar_nota(imagem_base64)
# Retorna: {'sucesso': True, 'dados': {...}} ou {'sucesso': False, 'erro': '...'}
```

### Modelos disponíveis
```python
from models import db, Transacao, get_transacoes_mes, get_totais_mes, get_gastos_por_categoria
```

---

## 🎯 REQUISITOS TÉCNICOS

### 1. Criar `app.py` - Aplicação Flask Principal
**Critério de aceite**: Aplicação Flask funcional com todas as rotas

```python
"""
Aplicação Flask para o GestorBot - Gestão Financeira para Restaurantes.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from datetime import datetime, date
import os
import base64
import logging

from config import Config, verificar_configuracoes
from models import db, Transacao, get_transacoes_mes, get_totais_mes, get_gastos_por_categoria
from services.groq_service import get_groq_service

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar banco de dados
db.init_app(app)

# Verificar configurações na inicialização
verificar_configuracoes()
```

---

### 2. Rota `GET /` - Tela Inicial (Home)
**Critério de aceite**: Renderiza template home.html

```python
@app.route('/')
def home():
    """Renderiza a tela inicial com botões de ação."""
    return render_template('home.html')
```

---

### 3. Rota `POST /upload-nota` - Processar Imagem com IA
**Critério de aceite**: Recebe imagem base64, processa com Groq, retorna JSON

```python
@app.route('/upload-nota', methods=['POST'])
def upload_nota():
    """
    Recebe imagem de nota fiscal e processa com IA.
    
    Request JSON:
        {"imagem": "data:image/jpeg;base64,..."}
    
    Response JSON (sucesso):
        {
            "sucesso": true,
            "dados": {
                "data": "2025-12-26",
                "estabelecimento": "CEASA",
                "valor_total": 245.80,
                "categoria": "Hortifruti"
            },
            "comprovante_url": "/static/uploads/nota_20251226_143022.jpg"
        }
    
    Response JSON (erro):
        {
            "sucesso": false,
            "erro": "Mensagem de erro"
        }
    """
    pass
```

**Lógica interna:**
1. Receber JSON com campo `imagem`
2. Validar que imagem não está vazia
3. Salvar imagem no disco (`static/uploads/`)
4. Chamar `get_groq_service().processar_nota(imagem_base64)`
5. Retornar resultado com URL do comprovante salvo

---

### 4. Rota `POST /transacao` - Salvar Transação
**Critério de aceite**: Valida dados, salva no banco, retorna confirmação

```python
@app.route('/transacao', methods=['POST'])
def criar_transacao():
    """
    Salva uma nova transação confirmada pelo usuário.
    
    Request JSON:
        {
            "tipo": "DESPESA",
            "valor": 245.80,
            "data": "2025-12-26",
            "categoria": "Hortifruti",
            "descricao": "Compras semanais",
            "estabelecimento": "CEASA Centro",
            "comprovante_url": "/static/uploads/nota_xxx.jpg"
        }
    
    Response JSON:
        {
            "sucesso": true,
            "id": 42,
            "mensagem": "Transação registrada com sucesso!"
        }
    """
    pass
```

**Validações obrigatórias:**
- `tipo` deve ser 'DESPESA' ou 'RECEITA'
- `valor` deve ser número positivo
- `data` deve ser formato válido
- `categoria` deve ser uma das válidas

---

### 5. Rota `GET /transacoes` - Listar Transações
**Critério de aceite**: Retorna lista filtrada de transações

```python
@app.route('/transacoes')
def listar_transacoes():
    """
    Lista transações com filtros opcionais.
    
    Query Parameters:
        - mes: int (1-12)
        - ano: int (ex: 2025)
        - tipo: 'DESPESA' ou 'RECEITA'
        - categoria: string
    
    Response JSON:
        {
            "transacoes": [...],
            "total": 10,
            "filtros": {"mes": 12, "ano": 2025}
        }
    """
    pass
```

---

### 6. Rota `GET /dashboard` - Painel Administrativo
**Critério de aceite**: Renderiza dashboard com dados calculados

```python
@app.route('/dashboard')
def dashboard():
    """
    Renderiza painel administrativo com métricas do mês.
    
    Query Parameters:
        - mes: int (default: mês atual)
        - ano: int (default: ano atual)
    
    Dados passados ao template:
        - faturamento: float (soma das receitas)
        - gastos: float (soma das despesas)
        - lucro: float (faturamento - gastos)
        - gastos_por_categoria: dict {categoria: valor}
        - mes_atual: int
        - ano_atual: int
    """
    pass
```

---

### 7. Rota `GET /receita` - Formulário de Receita
**Critério de aceite**: Renderiza formulário para lançar receita

```python
@app.route('/receita')
def form_receita():
    """Renderiza formulário para lançar receita (fechamento de caixa)."""
    return render_template('receita.html', categorias=['Vendas', 'Outros'])
```

---

### 8. Rota `GET /relatorio` - Gerar PDF
**Critério de aceite**: Gera e retorna PDF para download

```python
@app.route('/relatorio')
def gerar_relatorio():
    """
    Gera relatório mensal em PDF.
    
    Query Parameters:
        - mes: int (default: mês atual)
        - ano: int (default: ano atual)
    
    Response: Arquivo PDF para download
    """
    # Será implementado na Fase 6 - por enquanto retorna placeholder
    return jsonify({'mensagem': 'Relatório PDF será implementado na Fase 6'})
```

---

### 9. Função auxiliar `salvar_imagem()`
**Critério de aceite**: Salva base64 como arquivo e retorna URL

```python
def salvar_imagem(imagem_base64: str) -> str:
    """
    Salva imagem base64 no disco.
    
    Args:
        imagem_base64: String base64 (com ou sem prefixo data:image)
    
    Returns:
        str: URL relativa do arquivo salvo (ex: /static/uploads/nota_xxx.jpg)
    """
    # 1. Remover prefixo data:image se existir
    # 2. Decodificar base64
    # 3. Gerar nome único com timestamp
    # 4. Salvar em static/uploads/
    # 5. Retornar URL relativa
    pass
```

---

### 10. Inicialização do banco
**Critério de aceite**: Banco criado automaticamente na primeira execução

```python
def init_db():
    """Cria as tabelas do banco de dados se não existirem."""
    with app.app_context():
        db.create_all()
        logger.info("✅ Banco de dados inicializado")


if __name__ == '__main__':
    # Criar pasta de uploads se não existir
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Inicializar banco
    init_db()
    
    # Executar servidor
    debug_mode = os.getenv('FLASK_DEBUG', 'True') == 'True'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    logger.info(f"🚀 GestorBot iniciando em http://{host}:{port}")
    app.run(debug=debug_mode, host=host, port=port)
```

---

## 📐 PADRÕES A SEGUIR

### Respostas JSON Padronizadas
```python
# Sucesso
return jsonify({
    'sucesso': True,
    'dados': {...},
    'mensagem': 'Operação realizada com sucesso'
}), 200

# Erro de validação
return jsonify({
    'sucesso': False,
    'erro': 'Descrição do erro'
}), 400

# Erro interno
return jsonify({
    'sucesso': False,
    'erro': 'Erro interno do servidor'
}), 500
```

### Validação de Entrada
```python
data = request.get_json()
if not data:
    return jsonify({'sucesso': False, 'erro': 'JSON inválido'}), 400

campo_obrigatorio = data.get('campo')
if not campo_obrigatorio:
    return jsonify({'sucesso': False, 'erro': 'Campo X é obrigatório'}), 400
```

### Nomes de Arquivos de Upload
```python
# Formato: nota_YYYYMMDD_HHMMSS.jpg
from datetime import datetime
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"nota_{timestamp}.jpg"
```

---

## 🚫 NÃO FAZER

1. ❌ **NÃO** criar templates HTML (será na Fase 4)
2. ❌ **NÃO** implementar PDF real ainda (será na Fase 6)
3. ❌ **NÃO** adicionar autenticação (pós-MVP)
4. ❌ **NÃO** usar `print()` - usar `logging`
5. ❌ **NÃO** expor erros internos ao usuário - mensagens amigáveis
6. ❌ **NÃO** aceitar uploads sem validação de tipo/tamanho
7. ❌ **NÃO** criar rotas extras além das especificadas

---

## 📦 ENTREGÁVEIS

| # | Arquivo | Descrição |
|---|---------|-----------|
| 1 | `app.py` | Aplicação Flask completa com todas as rotas |

---

## ✅ VERIFICAÇÃO

### 1. Iniciar servidor
```bash
cd MONA_Controle_financeiro
python app.py
```

**Resultado esperado:**
```
INFO:__main__:✅ Banco de dados inicializado
INFO:__main__:🚀 GestorBot iniciando em http://0.0.0.0:5000
```

### 2. Testar rota home
```bash
curl http://localhost:5000/
```
**Resultado**: Erro de template (esperado - será criado na Fase 4)

### 3. Testar rota de transações (JSON)
```bash
curl http://localhost:5000/transacoes
```
**Resultado esperado:**
```json
{"transacoes": [], "total": 0, "filtros": {...}}
```

### 4. Testar criação de transação
```bash
curl -X POST http://localhost:5000/transacao \
  -H "Content-Type: application/json" \
  -d '{"tipo":"DESPESA","valor":100.00,"data":"2025-12-26","categoria":"Hortifruti","descricao":"Teste"}'
```
**Resultado esperado:**
```json
{"sucesso": true, "id": 1, "mensagem": "Transação registrada com sucesso!"}
```

### 5. Verificar banco de dados
```bash
python -c "from app import app, db; from models import Transacao; 
with app.app_context(): 
    print(f'Total: {Transacao.query.count()} transações')"
```

---

## 📝 NOTAS ADICIONAIS

### Sobre CORS
- Por padrão, Flask não precisa de CORS para templates próprios
- Se futuramente separar frontend, adicionar `flask-cors`

### Sobre uploads grandes
```python
# Já configurado em config.py:
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### Estrutura de resposta do upload-nota
```python
{
    "sucesso": True,
    "dados": {
        "data": "2025-12-26",
        "estabelecimento": "CEASA Centro",
        "valor_total": 245.80,
        "categoria": "Hortifruti"
    },
    "comprovante_url": "/static/uploads/nota_20251226_143022.jpg"
}
```
O frontend usará esses dados para preencher o formulário de conferência.

---

> **Próxima fase**: Fase 4 - Frontend Mobile-First (Templates HTML)
