# 🎨 PROMPT PARA V0 - Frontend GestorBot

> **Objetivo**: Criar um frontend premium em React/Next.js para sistema de gestão financeira de restaurante

---

## 📋 PROMPT PRINCIPAL

```
Crie um sistema de gestão financeira premium para restaurantes chamado "MONA Beach Club" usando Next.js 14, TypeScript, Tailwind CSS e shadcn/ui.

## 🎯 VISÃO GERAL

Sistema mobile-first para controle de despesas e receitas com OCR inteligente de notas fiscais. Design premium, profissional e extremamente intuitivo - uma experiência que impressiona à primeira vista.

## 🎨 DESIGN SYSTEM

### Cores
- Primary: Azul oceano (#0ea5e9) - remete a beach club
- Success: Verde esmeralda (#10b981) - receitas
- Danger: Vermelho coral (#ef4444) - despesas  
- Background: Gradiente suave do branco para azul claro
- Cards: Glassmorphism com blur e transparência
- Accent: Dourado sutil (#f59e0b) para destaques premium

### Tipografia
- Font: Inter ou Outfit (Google Fonts)
- Títulos: Bold, tracking tight
- Números: Tabular figures, monospace feel para valores

### Estilo Visual
- Glassmorphism em cards (backdrop-blur, bg-white/70)
- Sombras suaves e elevadas
- Bordas arredondadas (rounded-2xl)
- Micro-animações em hover (scale, shadow)
- Ícones Lucide React
- Gradientes sutis em botões e headers
- Dark mode elegante (opcional)

---

## 📱 PÁGINAS

### 1. HOME (/)
Layout: Tela cheia mobile-first

**Header:**
- Logo "MONA" estilizado com ícone de onda/praia
- Data atual formatada em português
- Avatar do usuário (placeholder)

**Ações Principais:**
- Card grande "📸 Nova Despesa" - gradiente vermelho/laranja
  - Ícone de câmera animado
  - Subtítulo: "Tire foto da nota fiscal"
  - Ao clicar: abre câmera/seletor de arquivo
  
- Card grande "💰 Fechar Caixa" - gradiente verde/esmeralda
  - Ícone de cifrão
  - Subtítulo: "Registrar receita do dia"
  - Ao clicar: navega para /receita

**Card de Resumo Rápido:**
- Mostra receitas, despesas e lucro do dia
- Valores com animação de contagem (count-up)
- Indicador visual de tendência (↑ ↓)

**Navegação:**
- Botão flutuante "📊 Ver Dashboard" com pulse animation
- Bottom navigation fixo para mobile

---

### 2. UPLOAD DE DESPESA (/despesa)

**Fluxo em Steps:**

**Step 1 - Captura:**
- Área de drop zone moderna com borda tracejada animada
- Botão "Tirar Foto" destacado
- Preview da imagem com zoom
- Suporte a PDF e imagens

**Step 2 - Processando (Modal/Overlay):**
- Skeleton loading elegante
- Animação de scanner passando pela imagem
- Texto: "Analisando nota fiscal com IA..."
- Barra de progresso animada

**Step 3 - Conferência:**
- Card com dados extraídos:
  - Data (input date com ícone)
  - Valor (input com máscara R$)
  - Estabelecimento (input text)
  - Categoria (select estilizado com ícones)
- Thumbnail da nota ao lado
- Indicador de confiança do OCR (badge)
- Botões: "Confirmar" (primary) e "Tentar Novamente" (ghost)

**Step 4 - Sucesso:**
- Animação de check (Lottie ou CSS)
- Confetti sutil
- "Despesa registrada!"
- Botão "Adicionar outra" ou "Ir para Dashboard"

---

### 3. RECEITA (/receita)

**Layout:**
- Header com título "Fechar Caixa"
- Subtítulo com data atual

**Formulário Premium:**
- Toggle group para tipo: Caixa | PIX | Cartão | Transferência
  - Ícones para cada tipo
  - Animação de seleção
  
- Input de valor estilo calculadora
  - Teclado numérico grande (mobile)
  - Formatação automática R$ 0,00
  
- Seletor de data com calendar picker moderno

- Campo opcional para descrição

- Upload de comprovante (opcional)
  - Ao anexar, faz OCR e preenche campos

**Botão Submit:**
- Grande, gradiente verde
- "Registrar Receita"
- Loading state com spinner

---

### 4. DASHBOARD (/dashboard)

**Header:**
- Navegação de mês: ◀ Dezembro 2025 ▶
- Animação de slide ao trocar mês

**Cards de Métricas (Grid 3 colunas no desktop, stack no mobile):**
1. Faturamento - Verde, ícone trending-up
2. Gastos - Vermelho, ícone trending-down  
3. Lucro - Azul/Dourado, ícone banknote

- Valores grandes, fonte bold
- Animação de contagem
- Sparkline mini gráfico de tendência

**Tabs de Categorias:**
```
[Despesas] [Receitas] [Histórico]
```
- Underline animado ao trocar
- Conteúdo com fade transition

**Aba Despesas:**
- Gráfico Doughnut/Pie interativo (Recharts)
- Cores por categoria
- Hover mostra valor e %
- Lista lateral com breakdown

**Aba Receitas:**
- Mesmo layout, cores verdes
- Categorias: Vendas, PIX, Cartão, etc.

**Aba Histórico:**
- Resumo visual do mês
- Cards de receita vs despesa

**Tabela de Transações:**
- Busca avançada colapsável:
  - Buscar por descrição
  - Filtrar por categoria (dropdown)
  - Filtrar por tipo (Receita/Despesa)
  - Range de valores
  - Range de datas
  - Botões: Buscar | Limpar

- Tabela responsiva:
  - Data | Descrição | Categoria (badge colorido) | Valor
  - Cores: verde para receita, vermelho para despesa
  - Hover com background sutil
  
- Paginação:
  - Seletor: 10 | 25 | 50 por página
  - Navegação: ◀ 1 2 3 ... 10 ▶
  - "Mostrando X de Y"

**Ação PDF:**
- Botão "📄 Baixar Relatório PDF"
- Download direto

---

## 🔌 API ENDPOINTS (Backend Flask existente)

```typescript
// Base URL: http://localhost:5000

// =====================
// TRANSAÇÕES
// =====================

// Criar transação (despesa ou receita)
POST /transacao
Body: { 
  tipo: "DESPESA" | "RECEITA",
  valor: number,
  data: "YYYY-MM-DD",
  categoria: string,
  descricao?: string,
  estabelecimento?: string,
  comprovante_url?: string
}
Response: { sucesso: boolean, id: number, mensagem: string }

// Listar transações com filtros
GET /transacoes?mes=12&ano=2025&tipo=DESPESA&categoria=Hortifruti
Response: { 
  transacoes: [{ id, tipo, valor, data, categoria, descricao, estabelecimento }],
  total: number,
  filtros: { mes, ano, tipo, categoria }
}

// Excluir transação
DELETE /transacao/{id}
Response: { sucesso: boolean, mensagem: string }

// =====================
// OCR (IA)
// =====================

// Upload nota fiscal + OCR para DESPESA
POST /upload-nota
Body: { imagem: "data:image/jpeg;base64,..." }  // ou PDF
Response: { 
  sucesso: boolean,
  dados: { data, valor, estabelecimento, categoria },
  comprovante_url: "/static/uploads/nota_xxx.jpg"
}

// Upload comprovante + OCR para RECEITA (PIX, transferência)
POST /upload-comprovante
Body: { arquivo: "data:image/jpeg;base64,..." }
Response: { 
  sucesso: boolean,
  url: "/static/uploads/comprovante_xxx.jpg",
  dados: { data, origem, valor, tipo_pagamento: "PIX" | "Transferência" }
}

// =====================
// DASHBOARD / MÉTRICAS
// =====================

// API JSON com totais do mês (para frontend separado)
GET /api/totais?mes=12&ano=2025
Response: {
  receitas: number,
  despesas: number,
  lucro: number,
  mes: number,
  ano: number
}

// Dashboard HTML (renderiza página, mas tem dados úteis)
GET /dashboard?mes=12&ano=2025&aba=despesas&page=1&per_page=10
Query params:
  - mes, ano: período
  - aba: "despesas" | "receitas" | "historico"
  - page, per_page: paginação
  - busca: texto livre
  - categoria, tipo: filtros
  - valor_min, valor_max: range
  - data_inicio, data_fim: período
Response: HTML

// =====================
// RELATÓRIO
// =====================

// Baixar relatório PDF do mês
GET /relatorio?mes=12&ano=2025
Response: application/pdf (download)

// =====================
// CATEGORIAS (constantes no config.py)
// =====================

// Categorias de DESPESA:
// - Frutos do Mar, Carnes e Aves, Hortifruti, Bebidas
// - Cervejas, Destilados, Vinhos, Laticínios
// - Embalagens, Limpeza, Manutenção, Gás, Outros

// Categorias de RECEITA:
// - Vendas, Caixa, PIX, Cartão, Transferência, Outros
```

---

## 📐 RESPONSIVIDADE

| Breakpoint | Layout |
|------------|--------|
| Mobile (<640px) | Stack vertical, bottom nav, cards full-width |
| Tablet (640-1024px) | Grid 2 colunas, sidebar colapsável |
| Desktop (>1024px) | Grid 3 colunas, sidebar fixa |

---

## ✨ MICRO-INTERAÇÕES

1. **Botões**: Scale 1.02 no hover, shadow-lg
2. **Cards**: Elevação aumenta no hover
3. **Inputs**: Border glow no focus (ring-2)
4. **Navegação**: Transitions suaves (300ms ease)
5. **Loading**: Skeleton com shimmer animation
6. **Sucesso**: Check animado + confetti
7. **Erro**: Shake animation + toast vermelho
8. **Números**: Count-up animation ao aparecer
9. **Gráficos**: Animação de entrada staggered
10. **Scroll**: Smooth scroll, anchor links

---

## 🎯 PRINCÍPIOS UX

1. **Zero Friction**: Mínimo de cliques para completar ação
2. **Feedback Imediato**: Toda ação tem resposta visual
3. **Mobile-First**: Funciona perfeitamente no celular
4. **Touch-Friendly**: Áreas de toque grandes (min 44px)
5. **Acessível**: Contraste adequado, labels em inputs
6. **Rápido**: Lazy loading, otimização de imagens
7. **Intuitivo**: Usuário não precisa de manual

---

## 📦 TECNOLOGIAS

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui (components)
- Recharts ou Chart.js (gráficos)
- React Hook Form + Zod (formulários)
- Framer Motion (animações)
- Lucide React (ícones)
- date-fns (datas em português)

---

## 🚀 COMEÇAR COM

Crie primeiro a página HOME com os dois cards de ação principais e o resumo rápido, usando glassmorphism e gradientes. O design deve impressionar imediatamente com aparência premium de fintech moderna.
```

---

## 💡 PROMPTS ADICIONAIS PARA REFINAR

### Para o Dashboard:
```
Crie um dashboard financeiro premium com:
- 3 cards de métricas (Faturamento, Gastos, Lucro) com glassmorphism
- Gráfico doughnut interativo por categoria
- Tabela de transações com busca avançada e paginação
- Navegação por mês com animação de slide
- Cores: verde para receitas, vermelho para despesas, azul para neutro
```

### Para o Fluxo de Upload:
```
Crie um fluxo de upload de nota fiscal em 4 steps:
1. Área de drop com preview
2. Loading com animação de scanner
3. Formulário de conferência dos dados extraídos
4. Tela de sucesso com confetti

Use transições suaves entre steps e skeleton loading.
```

### Para Mobile Navigation:
```
Crie uma bottom navigation fixa para mobile com 4 itens:
- Home (ícone casa)
- Nova Despesa (ícone câmera) - botão central destacado
- Receita (ícone cifrão)
- Dashboard (ícone gráfico)

Estilo: glassmorphism, ícone ativo com cor e label, animação de pulse no central.
```

---

## ⚠️ IMPORTANTE PARA V0

1. Peça **uma página por vez** para melhores resultados
2. Seja específico sobre **cores exatas** (hex codes)
3. Mencione **shadcn/ui** para componentes consistentes
4. Peça **versão mobile e desktop** separadamente se necessário
5. Use **imagens de referência** se tiver

---

> 🎉 Com este prompt, o V0 deve gerar um frontend que impressiona à primeira vista!
