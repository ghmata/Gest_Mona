# 🔐 Meta-Prompt: Planejamento de Sistema de Autenticação e Gerenciamento

> **IMPORTANTE**: Este prompt deve ser fornecido a um Arquiteto de Software para criar um plano detalhado de implementação.

---

## Instruções para o Arquiteto de Software

```markdown
Você é um **Arquiteto de Software Sênior** especializado em segurança de aplicações web e Flask.

Sua missão é criar um **plano de implementação completo e detalhado** para adicionar um sistema de autenticação (login/senha) e uma tela de gerenciamento ao sistema existente.

---

## ⚠️ ATENÇÃO CRÍTICA - SISTEMA EM PRODUÇÃO

> [!CAUTION]
> O sistema GestorBot **JÁ ESTÁ 100% FUNCIONAL** e em uso pela MONA Beach Club.
> 
> **REGRAS INVIOLÁVEIS:**
> - NÃO quebrar funcionalidades existentes
> - NÃO alterar estrutura de dados sem migração segura
> - NÃO remover ou modificar rotas existentes sem manter compatibilidade
> - TODA mudança deve ser incremental e reversível
> - TESTES obrigatórios antes de qualquer deploy

---

## 📋 CONTEXTO COMPLETO DO SISTEMA EXISTENTE

### Stack Tecnológica Atual
- **Backend**: Flask 2.x com Python 3.11+
- **Banco de Dados**: SQLAlchemy com SQLite
- **Frontend**: Templates Jinja2 + JavaScript vanilla
- **Hospedagem**: PythonAnywhere
- **Serviços externos**: Groq API para OCR

### Estrutura de Arquivos Relevantes
```
MONA_Controle_financeiro/
├── app.py              # Aplicação principal Flask (create_app factory)
├── config.py           # Configurações centralizadas (classe Config)
├── models.py           # Modelo Transacao com SQLAlchemy
├── routes/
│   ├── __init__.py     # Blueprints registrados
│   ├── main.py         # Rotas principais (dashboard, home)
│   ├── upload.py       # Upload de notas com OCR
│   ├── transacoes.py   # CRUD de transações
│   └── api.py          # Endpoints API
├── services/
│   ├── groq_service.py # Serviço de OCR
│   └── pdf_service.py  # Geração de relatórios PDF
├── templates/
│   ├── base.html       # Template base (navbar, footer)
│   ├── dashboard.html  # Dashboard principal
│   ├── home.html       # Página inicial
│   └── receita.html    # Formulário de receitas
└── static/
    ├── css/styles.css  # Estilos globais
    └── js/app.js       # JavaScript principal
```

### Modelo de Dados Atual
```python
class Transacao(db.Model):
    id: Integer (PK)
    tipo: String - 'DESPESA' ou 'RECEITA'
    valor: Float
    data: Date
    categoria: String
    subcategoria: String (opcional)
    descricao: Text (opcional)
    comprovante: String (caminho do arquivo)
    created_at: DateTime
    updated_at: DateTime
```

### Rotas Existentes (NÃO MODIFICAR SEM COMPATIBILIDADE)
| Método | Rota | Função |
|--------|------|--------|
| GET | `/` | Página inicial |
| GET | `/dashboard` | Dashboard com métricas |
| GET | `/receita` | Formulário de receita |
| POST | `/transacao` | Criar transação |
| GET | `/transacoes` | Listar transações |
| POST | `/upload-nota` | Upload + OCR |
| GET | `/relatorio` | Download PDF |
| DELETE | `/transacao/<id>` | Excluir transação |

---

## 🎯 REQUISITOS DA NOVA FUNCIONALIDADE

### 1. Sistema de Autenticação

#### 1.1 Modelo de Usuário
- Criar modelo `User` com:
  - `id`, `email`, `password_hash`, `nome`, `role` (admin/user), `ativo`, `created_at`
  - Usar Werkzeug para hash de senha (já disponível no Flask)
  - Relacionamento opcional com transações para auditoria futura

#### 1.2 Rotas de Autenticação
- `GET/POST /login` - Tela de login
- `POST /logout` - Logout
- `GET/POST /reset-password` - Recuperação de senha (opcional fase 2)

#### 1.3 Proteção de Rotas
- **TODAS** as rotas existentes devem requerer login
- Exceções: `/login`, `/static/*`, `/health-check`
- Usar Flask-Login ou implementação manual com sessões Flask

#### 1.4 Interface de Login
- Design consistente com o sistema atual (mobile-first)
- Mensagens de erro claras
- "Lembrar-me" opcional

### 2. Tela de Gerenciamento

#### 2.1 Dashboard Administrativo
Acessível apenas por usuários com role='admin':
- Gerenciar usuários (CRUD)
- Ver logs de atividade (opcional)
- Configurações do sistema

#### 2.2 Funcionalidades de Gerenciamento
- Listar todos os usuários
- Criar novo usuário
- Editar usuário (nome, email, role, ativo)
- Desativar usuário (soft delete)
- Resetar senha de usuário

---

## 📐 ESTRUTURA ESPERADA DO PLANO

Seu plano de implementação deve conter:

### Fase 1: Preparação (Sem impacto no sistema atual)
- [ ] Criar modelo User em `models.py`
- [ ] Criar migração segura do banco
- [ ] Criar templates de login e gerenciamento
- [ ] Criar arquivos de rotas em `routes/auth.py` e `routes/admin.py`

### Fase 2: Integração Controlada
- [ ] Registrar blueprints de auth e admin
- [ ] Adicionar middleware de autenticação
- [ ] Proteger rotas existentes com decorator

### Fase 3: Testes e Deploy
- [ ] Testes de regressão (funcionalidades existentes)
- [ ] Testes de autenticação
- [ ] Plano de rollback
- [ ] Deploy incremental

---

## 🚫 RESTRIÇÕES E GUARDRAILS

### NÃO FAZER:
1. ❌ Não usar pacotes de autenticação complexos (evitar overhead)
2. ❌ Não criar APIs novas desnecessárias
3. ❌ Não modificar estrutura das transações existentes
4. ❌ Não alterar fluxo de upload/OCR
5. ❌ Não criar nova base de dados (usar SQLite existente)

### OBRIGATÓRIO:
1. ✅ Manter compatibilidade total com sistema atual
2. ✅ Usar padrões já existentes no código (blueprints, Config class)
3. ✅ Documentar cada mudança
4. ✅ Criar usuário admin inicial em script separado
5. ✅ Implementar logging de tentativas de login

---

## 📦 ENTREGÁVEIS ESPERADOS

O plano deve especificar:

1. **Diagrama de fluxo** do processo de autenticação
2. **Schema do modelo User** com todos os campos
3. **Lista de arquivos** a criar/modificar com descrição do que fazer
4. **Ordem de implementação** com dependências
5. **Riscos identificados** e mitigações
6. **Plano de rollback** em caso de problemas
7. **Comandos de migração** do banco de dados
8. **Critérios de aceite** para cada funcionalidade

---

## 🔍 PERGUNTAS PARA O ARQUITETO RESPONDER

Antes de criar o plano, considere:

1. Usar Flask-Login ou implementar sessões manualmente?
2. Armazenar credenciais onde além do banco? (backup seguro)
3. Como migrar o banco sem perder dados de transações?
4. Qual estratégia para o primeiro deploy (feature flag)?
5. Como garantir que usuários logados não percam sessão em updates?

---

## ✅ CRITÉRIOS DE SUCESSO DO PLANO

O plano será considerado completo quando:

- [ ] Descreve EXATAMENTE quais arquivos criar/modificar
- [ ] Apresenta sequência clara de implementação
- [ ] Identifica pontos de risco com mitigações
- [ ] Inclui testes e critérios de aceite
- [ ] Mantém 100% compatibilidade com sistema atual
- [ ] Pode ser executado de forma incremental
- [ ] Inclui plano de rollback documentado

---

## 📝 FORMATO DA RESPOSTA

Gere o plano no formato Markdown estruturado com:
- Cabeçalhos hierárquicos (##, ###)
- Checklists para acompanhamento
- Blocos de código para exemplos
- Tabelas para comparações
- Diagramas Mermaid quando aplicável

O plano deve ser **autocontido** - qualquer desenvolvedor deve conseguir 
implementar seguindo apenas este documento.
```

---

## 🎯 Como Usar Este Meta-Prompt

1. **Copie** o bloco de código acima
2. **Cole** em uma nova conversa com a IA
3. **Aguarde** a geração do plano completo
4. **Revise** o plano gerado antes de implementar
5. **Ajuste** conforme necessidades específicas

---

## ⚡ Notas Importantes

- Este meta-prompt foi criado especificamente para o **GestorBot da MONA Beach Club**
- O sistema está **em produção** - toda cautela é necessária
- O plano gerado deve ser **revisado por um humano** antes da implementação
- Considere implementar em ambiente de staging primeiro
