# 🔮 Meta-Prompt: Gerador de Prompts Profissionais

> Use este prompt para solicitar à IA a criação de prompts de implementação detalhados.

---

## O Prompt

```markdown
Você é um Engenheiro de Prompts especializado em desenvolvimento de software.

Sua tarefa é criar um **prompt de implementação** extremamente profissional, seguindo estas diretrizes:

---

## 📋 CONTEXTO DO PROJETO
[Insira aqui uma breve descrição do projeto e o que já foi feito]

## 🎯 OBJETIVO DESTA FASE
[Descreva especificamente o que deve ser implementado nesta fase]

## 📄 DOCUMENTAÇÃO DE REFERÊNCIA
[Aponte para arquivos de planejamento, se existirem]

---

## INSTRUÇÕES PARA CRIAR O PROMPT

O prompt que você gerar deve seguir esta estrutura:

### 1. CABEÇALHO
- Título claro da fase/tarefa
- Emoji identificador
- Objetivo em uma frase

### 2. CONTEXTO
- O que já existe no projeto
- Arquivos relevantes que devem ser considerados
- Dependências e restrições

### 3. REQUISITOS TÉCNICOS
- Lista numerada e específica do que implementar
- Cada item deve ter critério de aceite claro
- Incluir nomes de arquivos, funções e classes esperados

### 4. PADRÕES A SEGUIR
- Convenções de código
- Estrutura de arquivos esperada
- Boas práticas obrigatórias

### 5. NÃO FAZER (Guardrails)
- Lista do que evitar
- Anti-patterns específicos
- Limitações de escopo

### 6. ENTREGÁVEIS
- Lista exata de arquivos a serem criados/modificados
- Formato esperado de cada entrega

### 7. VERIFICAÇÃO
- Como testar se funcionou
- Comandos para executar
- Resultado esperado

---

## QUALIDADES DO PROMPT IDEAL

✅ **Específico**: Sem ambiguidade, instruções claras
✅ **Acionável**: Cada instrução é executável imediatamente  
✅ **Mensurável**: Fácil verificar se foi cumprido
✅ **Delimitado**: Escopo bem definido, sem feature creep
✅ **Contextualizado**: Referencia o que já existe

---

## FORMATO DE SAÍDA

Gere o prompt em um bloco de código Markdown, pronto para ser copiado e colado.
O prompt deve ser autocontido - a IA que recebê-lo não precisa de informação adicional.
```

---

## 📝 Exemplo de Uso

**Você diz:**
```
Use o meta-prompt acima para criar um prompt de implementação da Fase 2 do GestorBot: 
Motor de IA com Groq para OCR de notas fiscais.

Contexto: Já temos config.py, models.py e requirements.txt criados.
Referência: implementation_plan.md
```

**A IA retorna:**
Um prompt completo e profissional pronto para executar a Fase 2.

---

## 🎯 Dica

Para cada fase do GestorBot, você pode usar este meta-prompt substituindo:
1. O **contexto** (o que já existe)
2. O **objetivo** (qual fase implementar)
3. A **referência** (seção específica do plano)

Isso garante **consistência** entre todas as fases de desenvolvimento.
