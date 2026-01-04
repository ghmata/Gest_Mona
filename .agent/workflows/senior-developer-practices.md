---
description: Boas práticas de programador sênior para consulta contínua durante o desenvolvimento
---

# 🎯 Guia de Boas Práticas - Desenvolvedor Sênior

Este documento serve como referência obrigatória para todas as decisões de código neste projeto.

---

## 1. PRINCÍPIOS FUNDAMENTAIS

### 1.1 SOLID
- **S**ingle Responsibility: Cada módulo/classe/função faz UMA coisa bem feita
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Subtipos devem ser substituíveis por seus tipos base
- **I**nterface Segregation: Interfaces específicas são melhores que uma geral
- **D**ependency Inversion: Dependa de abstrações, não de implementações

### 1.2 DRY (Don't Repeat Yourself)
- Nunca duplicar lógica de negócio
- Extrair funções utilitárias reutilizáveis
- Criar componentes genéricos quando padrão se repete 3+ vezes
- Usar constantes para valores que aparecem múltiplas vezes

### 1.3 KISS (Keep It Simple, Stupid)
- Código simples > código "esperto"
- Evitar over-engineering
- MVP primeiro, refatorar depois se necessário
- Clareza > brevidade

### 1.4 YAGNI (You Aren't Gonna Need It)
- Não implementar funcionalidades "para o futuro"
- Resolver o problema atual de forma extensível
- Features especulativas = dívida técnica

---

## 2. ORGANIZAÇÃO DE CÓDIGO

### 2.1 Estrutura de Pastas (Frontend React/Next.js)
```
src/
├── app/              # Rotas e páginas (Next.js App Router)
├── components/
│   ├── ui/           # Componentes primitivos (Button, Input, Card)
│   ├── features/     # Componentes de domínio (UserCard, PlanoForm)
│   └── layout/       # Componentes estruturais (Header, Sidebar)
├── hooks/            # Hooks customizados (ÚNICO local)
├── lib/
│   ├── api/          # Funções de chamada de API
│   ├── store/        # Gerenciamento de estado (Zustand/Redux)
│   ├── utils/        # Funções utilitárias puras
│   └── constants/    # Constantes e configurações
├── types/            # Tipos TypeScript compartilhados
└── styles/           # CSS global e tokens de design
```

### 2.2 Nomenclatura
| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Componentes | PascalCase | `UserProfileCard.tsx` |
| Hooks | camelCase com `use` | `useAuth.ts` |
| Utilitários | camelCase | `formatDate.ts` |
| Constantes | SCREAMING_SNAKE_CASE | `API_BASE_URL` |
| Tipos/Interfaces | PascalCase | `UserProfile`, `IUserService` |
| Arquivos CSS | kebab-case | `user-profile.css` |

### 2.3 Tamanho de Arquivos
- **Componentes**: Máximo 250 linhas (dividir se maior)
- **Funções**: Máximo 50 linhas (extrair sub-funções)
- **Arquivos de store**: Máximo 150 linhas (dividir por domínio)

---

## 3. TYPESCRIPT

### 3.1 Tipos Obrigatórios
```typescript
// ✅ CORRETO - Tipos explícitos
interface User {
  id: string
  name: string
  email: string
  createdAt: Date
}

const users: User[] = []
function getUser(id: string): User | undefined { ... }

// ❌ ERRADO - any, implicit any
const users: any = []
function getUser(id) { ... }
```

### 3.2 Evitar
- ❌ `any` - usar `unknown` se tipo desconhecido
- ❌ `as` casting desnecessário
- ❌ `!` non-null assertion sem necessidade
- ❌ Tipos em comentários ao invés de TypeScript

### 3.3 Preferir
- ✅ Interfaces para objetos públicos
- ✅ Types para unions e intersections
- ✅ Generics para código reutilizável
- ✅ `satisfies` para validação de tipos
- ✅ Discriminated unions para estados

---

## 4. REACT / NEXT.JS

### 4.1 Componentes
```typescript
// ✅ CORRETO - Props tipadas, componente focado
interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
  onClick?: () => void
  disabled?: boolean
}

export function Button({ children, variant = 'primary', onClick, disabled }: ButtonProps) {
  return (
    <button 
      className={cn(styles.button, styles[variant])}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}
```

### 4.2 Hooks
```typescript
// ✅ CORRETO - Hook com responsabilidade única
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : initialValue
  })

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value))
  }, [key, value])

  return [value, setValue] as const
}
```

### 4.3 Regras de Hooks
- ✅ Dependências corretas em useEffect/useMemo/useCallback
- ✅ Cleanup em useEffect quando necessário
- ✅ useMemo para cálculos pesados
- ✅ useCallback para funções passadas como props
- ❌ Hooks dentro de condicionais ou loops

### 4.4 Performance
- `React.memo()` para componentes que re-renderizam sem mudança de props
- Lazy loading com `dynamic()` para componentes pesados
- Virtualização para listas longas (>100 itens)
- Debounce em inputs de busca

---

## 5. GERENCIAMENTO DE ESTADO

### 5.1 Hierarquia de Estado
1. **Estado local** (useState) - UI específica do componente
2. **Estado elevado** (lifting state) - compartilhado entre irmãos
3. **Context** - estado global leve (tema, auth)
4. **Zustand/Redux** - estado global complexo

### 5.2 Zustand Best Practices
```typescript
// ✅ CORRETO - Actions separadas, selectors específicos
interface AuthStore {
  user: User | null
  isLoading: boolean
  login: (credentials: Credentials) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthStore>()((set) => ({
  user: null,
  isLoading: false,
  login: async (credentials) => {
    set({ isLoading: true })
    const user = await api.login(credentials)
    set({ user, isLoading: false })
  },
  logout: () => set({ user: null }),
}))

// Uso com selector para evitar re-renders
const user = useAuthStore((state) => state.user)
```

---

## 6. TRATAMENTO DE ERROS

### 6.1 API Calls
```typescript
// ✅ CORRETO - Try/catch com fallback
async function fetchPlanos(): Promise<Plano[]> {
  try {
    const response = await api.get('/planos')
    return response.data
  } catch (error) {
    if (error instanceof ApiError) {
      toast.error(error.message)
    } else {
      toast.error('Erro ao carregar planos')
      console.error('Fetch planos error:', error)
    }
    return [] // Fallback seguro
  }
}
```

### 6.2 Error Boundaries
```typescript
// ✅ Sempre ter Error Boundary no root
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
```

### 6.3 Princípios
- Nunca falhar silenciosamente
- Sempre dar feedback ao usuário
- Logs estruturados para debugging
- Graceful degradation quando possível

---

## 7. ACESSIBILIDADE (a11y)

### 7.1 Obrigatório
- ✅ `alt` em todas as imagens
- ✅ Labels em todos os inputs
- ✅ `role` em elementos interativos não-nativos
- ✅ `tabIndex` para navegação por teclado
- ✅ Contraste mínimo 4.5:1 para texto
- ✅ Focus visible em elementos interativos

### 7.2 Elementos Interativos
```tsx
// ✅ CORRETO
<div 
  role="button" 
  tabIndex={0} 
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
  aria-label="Abrir menu"
>
  <MenuIcon />
</div>

// ❌ ERRADO
<div onClick={handleClick}>
  <MenuIcon />
</div>
```

---

## 8. SEGURANÇA

### 8.1 Frontend
- ❌ Nunca armazenar secrets no código
- ❌ Nunca confiar em input do usuário
- ✅ Sanitizar HTML dinâmico
- ✅ Usar HTTPS sempre
- ✅ CSP headers quando possível
- ✅ Validação client-side + server-side

### 8.2 Variáveis de Ambiente
```bash
# .env.local (NUNCA commitar)
NEXT_PUBLIC_API_URL=https://api.example.com
API_SECRET_KEY=secret  # Apenas server-side
```

---

## 9. COMMITS E VERSIONAMENTO

### 9.1 Conventional Commits
```
<tipo>(<escopo>): <descrição>

feat(auth): adicionar login com Google
fix(wizard): corrigir validação de step 2
refactor(store): separar stores por domínio
docs(readme): atualizar instruções de instalação
style(button): ajustar padding do botão primário
test(plano): adicionar testes de geração
chore(deps): atualizar dependências
```

### 9.2 Branches
- `main` - produção
- `develop` - desenvolvimento
- `feature/nome-feature` - nova funcionalidade
- `fix/nome-bug` - correção de bug
- `refactor/nome` - refatoração

---

## 10. TESTES

### 10.1 Pirâmide de Testes
1. **Unit** (70%) - Funções e hooks isolados
2. **Integration** (20%) - Componentes com suas dependências
3. **E2E** (10%) - Fluxos críticos do usuário

### 10.2 O que testar
- ✅ Lógica de negócio
- ✅ Edge cases
- ✅ Comportamento do usuário
- ❌ Implementação interna
- ❌ Estilos CSS
- ❌ Bibliotecas de terceiros

---

## 11. CODE REVIEW CHECKLIST

Antes de submeter código, verificar:

### Funcionalidade
- [ ] O código faz o que deveria?
- [ ] Edge cases foram considerados?
- [ ] Erros são tratados adequadamente?

### Qualidade
- [ ] Nomes são descritivos e consistentes?
- [ ] Há código duplicado?
- [ ] Componentes têm responsabilidade única?
- [ ] Tipos TypeScript estão completos?

### Performance
- [ ] Há renderizações desnecessárias?
- [ ] Chamadas de API são otimizadas?
- [ ] Assets são lazy loaded quando possível?

### Acessibilidade
- [ ] Elementos têm labels/roles corretos?
- [ ] Navegação por teclado funciona?

---

## 12. DOCUMENTAÇÃO

### 12.1 Quando documentar
- Lógica de negócio complexa
- Decisões de arquitetura não-óbvias
- APIs públicas/exportadas
- Configurações e setup

### 12.2 JSDoc para funções públicas
```typescript
/**
 * Gera um plano de aula baseado nos parâmetros fornecidos.
 * 
 * @param params - Parâmetros de geração do plano
 * @returns Promise com o plano gerado ou null em caso de erro
 * @throws {ValidationError} Se os parâmetros forem inválidos
 * 
 * @example
 * const plano = await gerarPlano({
 *   disciplina: 'Matemática',
 *   serie: '5º Ano',
 *   duracao: '50 min'
 * })
 */
export async function gerarPlano(params: PlanoParams): Promise<Plano | null> {
  // ...
}
```

---

## 13. PERFORMANCE WEB

### 13.1 Core Web Vitals
- **LCP** (Largest Contentful Paint) < 2.5s
- **FID** (First Input Delay) < 100ms
- **CLS** (Cumulative Layout Shift) < 0.1

### 13.2 Otimizações
- Imagens: WebP, lazy loading, srcset
- Fonts: preload, font-display: swap
- JavaScript: code splitting, tree shaking
- CSS: critical CSS inline, async load

---

## 14. LOGS E MONITORAMENTO

### 14.1 Níveis de Log
- `error` - Erros que afetam funcionalidade
- `warn` - Situações potencialmente problemáticas
- `info` - Eventos importantes de negócio
- `debug` - Informações para desenvolvimento

### 14.2 Estrutura
```typescript
// ✅ CORRETO - Log estruturado
logger.error('Falha ao gerar plano', {
  userId: user.id,
  planoParams: params,
  error: error.message,
  stack: error.stack
})

// ❌ ERRADO
console.log('erro: ' + error)
```

---

## RESUMO: REGRAS DE OURO

1. **Código limpo** > código rápido de escrever
2. **Tipos fortes** > flexibilidade com `any`
3. **Componentes pequenos** > componentes monolíticos
4. **Tratamento de erro** > assumir que tudo funciona
5. **Acessibilidade** > velocidade de entrega
6. **Testes** > debugging manual
7. **Documentação** > conhecimento implícito
8. **Revisão de código** > merge direto
9. **Simplicidade** > complexidade desnecessária
10. **Iteração** > perfeição inicial

---

// turbo-all
