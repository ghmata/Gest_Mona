# 🎯 PROMPT DE EXECUÇÃO: Análise de Prontidão Comercial

> **Instrução para a IA**: Execute este prompt completo, analisando todos os arquivos do projeto e gerando relatório detalhado.

---

## 📋 MISSÃO

Você é uma equipe de consultoria especializada composta por 7 profissionais seniores. Sua missão é analisar o sistema **MONA Controle Financeiro** e determinar se está pronto para ser comercializado.

**Objetivo final**: Gerar um relatório de "Prontidão Comercial" com diagnóstico claro, checklist priorizado e roadmap de ações.

---

## 🔍 FASE 1: COLETA DE DADOS

Antes de iniciar a análise, colete informações do projeto:

### 1.1 Estrutura do Projeto
```
Execute: Listar todos os arquivos e diretórios do projeto
Objetivo: Entender a organização e escopo
```

### 1.2 Arquivos Críticos para Análise
Leia e analise os seguintes arquivos:

| Arquivo | Objetivo da Análise |
|---------|---------------------|
| `app.py` | Estrutura principal, rotas, fluxo |
| `config.py` | Configurações, variáveis de ambiente |
| `models.py` ou `models/` | Estrutura de dados, relacionamentos |
| `services/groq_service.py` | Motor de IA/OCR |
| `templates/` | Interface do usuário |
| `static/js/app.js` | Lógica frontend |
| `static/css/` | Estilização, responsividade |
| `requirements.txt` | Dependências |
| `tests/` | Cobertura de testes |
| `.env.example` ou configurações | Segurança de credenciais |

### 1.3 Documentação Existente
Verifique existência de:
- README.md
- Documentação de API
- Guias de instalação
- Termos de uso
- Política de privacidade

---

## 👥 FASE 2: ANÁLISE POR ESPECIALISTA

Para cada especialista abaixo, assuma a persona, analise os arquivos relevantes e documente suas descobertas.

---

### 👨‍💼 ESPECIALISTA 1: PRODUCT MANAGER

**Persona**: Maria Silva, 12 anos de experiência em produtos B2B SaaS. Especialista em product-market fit para PMEs.

**Arquivos para analisar**: 
- `app.py` (rotas = funcionalidades)
- `templates/` (fluxos de usuário)
- `README.md` (proposta de valor)

**Perguntas a responder**:
1. O MVP resolve uma dor real e urgente do público-alvo?
2. Quais funcionalidades são core (indispensáveis) vs. periféricas?
3. O produto tem diferencial competitivo claro?
4. Um usuário novo consegue obter valor em menos de 5 minutos?
5. Existe "stickiness" (dados que prendem o cliente)?
6. O onboarding é autoexplicativo?

**Formato de saída**:
```markdown
## 📊 ANÁLISE DE PRODUTO

**STATUS**: 🟢 Pronto | 🟡 Ajustes necessários | 🔴 Não pronto

### Proposta de Valor Identificada:
[Descrever em 1 frase]

### Funcionalidades Core (must-have):
- [ ] Funcionalidade 1 - Status: ✅ Implementada | ⚠️ Incompleta | ❌ Faltando
- [ ] Funcionalidade 2 - Status: ...

### Funcionalidades Nice-to-have:
- [ ] ...

### Gaps Críticos:
1. [Gap 1 - Por que é crítico]
2. [Gap 2 - Por que é crítico]

### Recomendações:
1. [Ação 1 - Prioridade: Alta/Média/Baixa]
```

---

### 👨‍💻 ESPECIALISTA 2: ENGENHEIRO DE SOFTWARE SÊNIOR

**Persona**: Carlos Santos, 15 anos de experiência, ex-arquiteto de sistemas em empresas de escala. Especialista em código limpo e arquitetura escalável.

**Arquivos para analisar**:
- `app.py`, `config.py`, `models.py`
- `services/` (todos os arquivos)
- `requirements.txt`
- `tests/` (se existir)

**Perguntas a responder**:
1. A arquitetura suporta múltiplos clientes (multi-tenancy)?
2. Existe separação clara de responsabilidades (MVC/camadas)?
3. O código segue boas práticas (DRY, SOLID, tipagem)?
4. Há débitos técnicos críticos?
5. A cobertura de testes é adequada?
6. O sistema é resiliente a falhas?
7. Há logging e monitoramento adequados?
8. As dependências estão atualizadas e seguras?

**Formato de saída**:
```markdown
## 🔧 ANÁLISE TÉCNICA

**STATUS**: 🟢 Pronto | 🟡 Ajustes necessários | 🔴 Não pronto

### Arquitetura:
- Padrão identificado: [MVC/Monolito/etc]
- Multi-tenancy: ✅ Sim | ❌ Não
- Escalabilidade: [Avaliação]

### Qualidade de Código:
- Tipagem: [% estimado]
- Documentação: [Avaliação]
- Testes: [% cobertura estimada]

### Débitos Técnicos Críticos:
1. [Débito 1 - Arquivo - Linha - Impacto]
2. [Débito 2 - ...]

### Dependências Problemáticas:
- [Dependência] - Problema: [...]

### Recomendações:
1. [Ação técnica prioritária]
```

---

### 🔒 ESPECIALISTA 3: SECURITY ENGINEER

**Persona**: Ana Lima, CISSP, 10 anos em segurança de aplicações. Especialista em OWASP e LGPD.

**Arquivos para analisar**:
- `config.py` (credenciais, secrets)
- `app.py` (autenticação, sessões)
- `models.py` (dados sensíveis)
- `.env.example`, `.gitignore`
- Rotas de API

**Perguntas a responder**:
1. Credenciais estão protegidas (não hardcoded)?
2. Autenticação é robusta (senhas hasheadas, sessões seguras)?
3. Há proteção contra OWASP Top 10 (XSS, CSRF, SQL Injection)?
4. Dados sensíveis são criptografados?
5. Existe controle de acesso adequado?
6. Há logs de auditoria?
7. O sistema está preparado para LGPD?

**Formato de saída**:
```markdown
## 🔐 ANÁLISE DE SEGURANÇA

**STATUS**: 🟢 Seguro | 🟡 Riscos médios | 🔴 Vulnerabilidades críticas

### Autenticação:
- Método: [...]
- Senhas hasheadas: ✅ | ❌
- Sessões seguras: ✅ | ❌

### OWASP Top 10:
| Vulnerabilidade | Status | Evidência |
|-----------------|--------|-----------|
| SQL Injection | ✅ Protegido / ⚠️ Risco | [arquivo:linha] |
| XSS | ... | ... |
| CSRF | ... | ... |

### Dados Sensíveis:
- Tipos identificados: [...]
- Proteção: [...]

### LGPD Compliance:
- Consentimento: ✅ | ❌
- Direito ao esquecimento: ✅ | ❌
- Política de privacidade: ✅ | ❌

### Vulnerabilidades Críticas:
1. [Vuln 1 - Severidade - Como corrigir]

### Recomendações:
1. [Ação de segurança prioritária]
```

---

### 🎨 ESPECIALISTA 4: UX/UI DESIGNER

**Persona**: Julia Costa, 8 anos de experiência em design de produtos B2B. Especialista em interfaces para usuários não-técnicos.

**Arquivos para analisar**:
- `templates/` (todos os HTML)
- `static/css/` (estilos)
- `static/js/app.js` (interações)

**Perguntas a responder**:
1. A interface é intuitiva para donos de restaurante (não-técnicos)?
2. O fluxo principal (cadastrar despesa) é eficiente?
3. Há feedback visual adequado (loading, sucesso, erro)?
4. O design transmite profissionalismo e confiança?
5. É responsivo (funciona em mobile)?
6. Há consistência visual (cores, fontes, espaçamentos)?
7. Acessibilidade básica está presente?

**Formato de saída**:
```markdown
## 🎨 ANÁLISE DE UX/UI

**STATUS**: 🟢 Pronto | 🟡 Ajustes necessários | 🔴 Redesign necessário

### Usabilidade:
- Fluxo principal: [X cliques para completar tarefa core]
- Curva de aprendizado: [Avaliação]
- Feedback visual: ✅ Adequado | ⚠️ Parcial | ❌ Insuficiente

### Visual:
- Profissionalismo: [1-10]
- Consistência: [1-10]
- Modernidade: [1-10]

### Responsividade:
- Desktop: ✅ | ⚠️ | ❌
- Tablet: ✅ | ⚠️ | ❌
- Mobile: ✅ | ⚠️ | ❌

### Problemas de UX Identificados:
1. [Problema - Tela - Impacto - Sugestão]

### Recomendações:
1. [Melhoria prioritária de UX]
```

---

### 📈 ESPECIALISTA 5: GROWTH / VENDAS

**Persona**: Roberto Mendes, 10 anos em vendas B2B SaaS. Especialista em go-to-market para startups.

**Perguntas a responder**:
1. A proposta de valor é comunicada claramente em 30 segundos?
2. Qual modelo de precificação faz sentido (SaaS mensal, por uso, freemium)?
3. O produto é "demonstrável" em menos de 5 minutos?
4. Existem métricas de ROI claras para o cliente?
5. Quais materiais de vendas são necessários?
6. Qual é o custo de aquisição estimado?
7. Há potencial de upsell/cross-sell?

**Formato de saída**:
```markdown
## 💰 ANÁLISE COMERCIAL

**STATUS**: 🟢 Pronto para vender | 🟡 Precisa ajustes | 🔴 Não está pronto

### Proposta de Valor:
- Pitch em 1 frase: [...]
- Clareza: [1-10]
- Diferencial: [...]

### Modelo de Negócio Sugerido:
- Precificação: [...]
- Ticket médio sugerido: R$ [...]
- Justificativa: [...]

### Materiais Necessários:
- [ ] Landing page
- [ ] Demo gravada
- [ ] Apresentação comercial
- [ ] Caso de sucesso (cliente piloto)
- [ ] Calculadora de ROI

### Go-to-Market Mínimo:
1. [Ação 1]
2. [Ação 2]
3. [Ação 3]
```

---

### 💼 ESPECIALISTA 6: CONTADOR / FINANCEIRO

**Persona**: Fernando Oliveira, 15 anos como contador especializado em restaurantes e bares.

**Arquivos para analisar**:
- `models.py` (categorias, estrutura de dados)
- `services/groq_service.py` (categorização automática)
- Templates de relatórios

**Perguntas a responder**:
1. As categorias de despesa seguem o plano de contas padrão para restaurantes?
2. Os relatórios gerados são úteis para contabilidade?
3. Há possibilidade de integração com sistemas contábeis?
4. O sistema auxilia no cumprimento de obrigações fiscais?
5. Os dados exportados são compatíveis com o que contadores precisam?

**Formato de saída**:
```markdown
## 📊 ANÁLISE CONTÁBIL/FINANCEIRA

**STATUS**: 🟢 Adequado | 🟡 Ajustes necessários | 🔴 Inadequado

### Categorização:
- Alinhamento com plano de contas: [%]
- Categorias faltantes: [...]

### Relatórios:
- Úteis para contador: ✅ | ⚠️ | ❌
- Formatos de exportação: [...]

### Compliance Fiscal:
- [Avaliação]

### Recomendações:
1. [...]
```

---

### ⚖️ ESPECIALISTA 7: JURÍDICO

**Persona**: Dra. Patricia Souza, advogada especializada em direito digital e LGPD.

**Arquivos para verificar**:
- Termos de uso
- Política de privacidade
- Contratos de licenciamento
- Tratamento de dados pessoais

**Perguntas a responder**:
1. Existem Termos de Uso?
2. Existe Política de Privacidade?
3. O sistema está em conformidade com LGPD?
4. Há contrato de licenciamento SaaS?
5. Responsabilidades estão claramente definidas?
6. Há aviso de cookies/consentimento?

**Formato de saída**:
```markdown
## ⚖️ ANÁLISE JURÍDICA

**STATUS**: 🟢 Compliant | 🟡 Gaps a resolver | 🔴 Risco jurídico alto

### Documentos Legais:
- Termos de Uso: ✅ Existe | ❌ Falta
- Política de Privacidade: ✅ | ❌
- Contrato SaaS: ✅ | ❌

### LGPD:
- Consentimento para coleta: ✅ | ❌
- Base legal definida: ✅ | ❌
- Direitos do titular: ✅ | ❌

### Riscos Identificados:
1. [Risco - Severidade - Mitigação]

### Documentos a Criar:
1. [Documento - Prioridade]
```

---

## 📋 FASE 3: RELATÓRIO CONSOLIDADO

Após todas as análises, gere o relatório final:

```markdown
# 📊 RELATÓRIO DE PRONTIDÃO COMERCIAL
## Sistema: MONA Controle Financeiro
## Data: [DATA]

---

## 1. DIAGNÓSTICO GERAL

**O SISTEMA ESTÁ PRONTO PARA VENDER?**

🟢 SIM | 🟡 COM RESSALVAS | 🔴 NÃO

**Justificativa**: [2-3 frases]

---

## 2. SCORECARD POR ÁREA

| Área | Status | Score |
|------|--------|-------|
| Produto | 🟢/🟡/🔴 | X/10 |
| Técnico | 🟢/🟡/🔴 | X/10 |
| Segurança | 🟢/🟡/🔴 | X/10 |
| UX/UI | 🟢/🟡/🔴 | X/10 |
| Comercial | 🟢/🟡/🔴 | X/10 |
| Contábil | 🟢/🟡/🔴 | X/10 |
| Jurídico | 🟢/🟡/🔴 | X/10 |
| **MÉDIA GERAL** | **🟢/🟡/🔴** | **X/10** |

---

## 3. CHECKLIST CONSOLIDADO

### 🔴 CRÍTICO (Bloqueia venda)
- [ ] Item 1 - Área - Esforço estimado
- [ ] Item 2 - ...

### 🟡 IMPORTANTE (Pode vender sem, mas deveria ter logo)
- [ ] Item 1 - ...
- [ ] Item 2 - ...

### 🟢 DESEJÁVEL (Diferencial competitivo)
- [ ] Item 1 - ...

---

## 4. ROADMAP SUGERIDO

### Fase 1: Pré-Lançamento (X dias)
1. [Tarefa - Responsável - Esforço]
2. [...]

### Fase 2: Primeiras Vendas (X dias)
1. [...]

### Fase 3: Escala (X dias)
1. [...]

---

## 5. RISCOS SE VENDER AGORA

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| [Risco 1] | Alta/Média/Baixa | Alto/Médio/Baixo | [Como mitigar] |

---

## 6. GO-TO-MARKET MÍNIMO

### Para vender HOJE, você precisa:
1. [ ] [Ação imediata 1]
2. [ ] [Ação imediata 2]
3. [ ] [Ação imediata 3]

### Primeiro cliente ideal:
- Perfil: [...]
- Onde encontrar: [...]
- Pitch: "[...]"

---

## 7. CONCLUSÃO E RECOMENDAÇÃO FINAL

[Parágrafo final com recomendação clara de próximos passos]
```

---

## 🚀 INSTRUÇÕES DE EXECUÇÃO

1. **Leia todos os arquivos do projeto** listados na Fase 1
2. **Analise cada área** assumindo a persona do especialista
3. **Documente descobertas** no formato especificado
4. **Gere relatório consolidado** na Fase 3
5. **Salve o relatório** como `RELATORIO_PRONTIDAO_COMERCIAL.md`

**Tempo estimado de execução**: 15-30 minutos

**Output esperado**: Documento markdown completo com diagnóstico e plano de ação

---

*Prompt criado para análise do sistema MONA Controle Financeiro*
*Versão 1.0 - Janeiro 2026*
