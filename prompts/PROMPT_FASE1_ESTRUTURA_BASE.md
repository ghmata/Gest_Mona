# 🏗️ Fase 1: Estrutura Base e Backend

> **Objetivo**: Configurar a fundação do projeto GestorBot com estrutura de pastas, configurações e modelos de dados.

---

## 🎭 ROLE

Você é um **Desenvolvedor Python Sênior** especializado em:
- Arquitetura de aplicações Flask
- Modelagem de dados com SQLAlchemy
- Configuração de projetos seguindo boas práticas
- Código limpo, documentado e manutenível

**Seu estilo de código:**
- Type hints em todas as funções
- Docstrings em português
- Nomes descritivos (snake_case para variáveis, PascalCase para classes)
- Tratamento de erros robusto

---

## 📋 CONTEXTO

### Projeto
**GestorBot** é um sistema de gestão financeira para restaurantes com OCR inteligente de notas fiscais.

### O que já existe
- 📄 `implementation_plan.md` - Plano detalhado de implementação
- 📄 `META_PROMPT_GERADOR.md` - Template para gerar prompts

### Tecnologias definidas
- **Backend**: Python 3.11+ com Flask
- **Banco de Dados**: SQLite com SQLAlchemy ORM
- **IA/OCR**: Groq API (LLaMA Vision)
- **Frontend**: HTML + Bootstrap 5 (mobile-first)

### Localização do projeto
```
c:\Users\gabri\OneDrive\Desktop\Freela\SERVIÇOS\MONA_Controle_financeiro\
```

---

## 🎯 REQUISITOS TÉCNICOS

### 1. Criar `requirements.txt`
**Critério de aceite**: Arquivo contém todas as dependências necessárias

```
flask==3.0.0
flask-sqlalchemy==3.1.1
python-dotenv==1.0.0
groq==0.4.2
fpdf2==2.7.6
pillow==10.1.0
werkzeug==3.0.1
```

---

### 2. Criar `.env.example`
**Critério de aceite**: Arquivo documenta todas as variáveis de ambiente necessárias

```env
# Chave da API Groq (obrigatório para OCR)
GROQ_API_KEY=sua_chave_groq_aqui

# Chave secreta do Flask (gere uma aleatória para produção)
SECRET_KEY=sua_chave_secreta_aqui

# Modo de debug
FLASK_DEBUG=True

# Host e Porta
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

---

### 3. Criar `config.py`
**Critério de aceite**: Classe `Config` centraliza todas as configurações

```python
# Deve conter:
# - SECRET_KEY (do .env ou fallback)
# - SQLALCHEMY_DATABASE_URI (sqlite:///gestor.db)
# - SQLALCHEMY_TRACK_MODIFICATIONS = False
# - UPLOAD_FOLDER (caminho para static/uploads)
# - MAX_CONTENT_LENGTH (16MB)
# - ALLOWED_EXTENSIONS ({'png', 'jpg', 'jpeg', 'gif', 'webp'})
# - GROQ_API_KEY (do .env)
# - GROQ_MODEL ('llama-3.2-90b-vision-preview')
# - CATEGORIAS_DESPESA (lista com 7 categorias)
# - Função verificar_configuracoes() que valida se GROQ_API_KEY existe
```

---

### 4. Criar `models.py`
**Critério de aceite**: Modelo `Transacao` com todos os campos e métodos auxiliares

```python
class Transacao(db.Model):
    __tablename__ = 'transacoes'
    
    # Campos obrigatórios:
    id              # Integer, primary_key
    tipo            # String(10), NOT NULL - 'DESPESA' ou 'RECEITA'
    valor           # Float, NOT NULL
    data            # DateTime, NOT NULL, default=utcnow
    categoria       # String(50), NOT NULL
    descricao       # String(200), nullable
    estabelecimento # String(100), nullable
    comprovante_url # String(500), nullable
    status          # String(20), default='CONFIRMADO'
    created_at      # DateTime, default=utcnow
    
    # Métodos obrigatórios:
    def to_dict(self) -> dict  # Converte para dicionário
    
# Funções auxiliares obrigatórias:
def get_transacoes_mes(ano: int, mes: int) -> list
def get_totais_mes(ano: int, mes: int) -> dict  # {receitas, despesas, lucro}
def get_gastos_por_categoria(ano: int, mes: int) -> dict
```

---

### 5. Criar estrutura de pastas
**Critério de aceite**: Estrutura criada conforme especificação

```
MONA_Controle_financeiro/
├── services/
│   └── __init__.py
├── templates/
│   └── (vazio por enquanto)
├── static/
│   ├── css/
│   └── uploads/
├── utils/
│   └── __init__.py
└── instance/
    └── (criado automaticamente pelo SQLite)
```

---

### 6. Criar `.gitignore`
**Critério de aceite**: Ignora arquivos sensíveis e desnecessários

```gitignore
# Ambiente
.env
venv/
__pycache__/
*.pyc

# Banco de dados
instance/
*.db

# Uploads de usuários
static/uploads/*
!static/uploads/.gitkeep

# IDE
.vscode/
.idea/
```

---

## 📐 PADRÕES A SEGUIR

### Convenções de código
- Python: PEP 8, docstrings em português
- Nomes de variáveis: snake_case
- Nomes de classes: PascalCase
- Comentários explicativos em funções complexas

### Estrutura de imports
```python
# 1. Bibliotecas padrão
from datetime import datetime
import os

# 2. Bibliotecas externas
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# 3. Imports locais
from config import Config
```

### Tratamento de erros
- Sempre usar try/except em operações de I/O
- Logar erros com mensagens descritivas
- Retornar mensagens amigáveis ao usuário

---

## 🚫 NÃO FAZER

1. ❌ **NÃO** criar rotas Flask ainda (será na Fase 3)
2. ❌ **NÃO** implementar o serviço Groq ainda (será na Fase 2)
3. ❌ **NÃO** criar templates HTML ainda (será na Fase 4)
4. ❌ **NÃO** hardcodar a API key no código
5. ❌ **NÃO** usar `print()` para debug - usar `logging`
6. ❌ **NÃO** criar dados de teste/seed nesta fase

---

## 📦 ENTREGÁVEIS

| # | Arquivo | Descrição |
|---|---------|-----------|
| 1 | `requirements.txt` | Dependências Python |
| 2 | `.env.example` | Template de variáveis de ambiente |
| 3 | `config.py` | Configurações centralizadas |
| 4 | `models.py` | Modelo Transacao + funções auxiliares |
| 5 | `.gitignore` | Arquivos ignorados pelo Git |
| 6 | `services/__init__.py` | Pacote de serviços (vazio) |
| 7 | `utils/__init__.py` | Pacote de utilitários (vazio) |
| 8 | `static/uploads/.gitkeep` | Mantém pasta no Git |

---

## ✅ VERIFICAÇÃO

### 1. Testar imports
```bash
cd MONA_Controle_financeiro
python -c "from config import Config; print('Config OK')"
python -c "from models import db, Transacao; print('Models OK')"
```

### 2. Verificar estrutura
```bash
# Listar arquivos criados
dir /s /b *.py *.txt *.example
```

### 3. Resultado esperado
- Todos os imports funcionam sem erro
- Nenhuma API key exposta no código
- Estrutura de pastas completa

---

## 📝 NOTAS ADICIONAIS

- O banco SQLite será criado automaticamente na primeira execução do Flask
- A pasta `instance/` é onde o SQLite armazena o arquivo `.db`
- O arquivo `.env` real deve ser criado manualmente pelo desenvolvedor copiando `.env.example`

---

> **Próxima fase**: Fase 2 - Motor de IA (Groq OCR)
