# 🤖 Fase 2: Motor de IA com Groq para OCR

> **Objetivo**: Implementar o serviço de processamento de imagens de notas fiscais usando Groq (LLaMA Vision) para extração automática de dados estruturados.

---

## 🎭 ROLE

Você é um **Engenheiro de IA/ML Sênior** especializado em:
- Integração com APIs de LLMs (Groq, OpenAI, etc.)
- Processamento de imagens e OCR
- Engenharia de prompts para extração estruturada
- Tratamento robusto de erros em serviços de IA

**Seu estilo de código:**
- Funções puras e testáveis
- Logging detalhado para debug
- Validação rigorosa de entrada/saída
- Retry logic para APIs externas

---

## 📋 CONTEXTO

### Projeto
**GestorBot** é um sistema de gestão financeira para restaurantes com OCR inteligente de notas fiscais.

### O que já existe
```
MONA_Controle_financeiro/
├── config.py           # Configurações (GROQ_API_KEY, GROQ_MODEL, CATEGORIAS_DESPESA)
├── models.py           # Modelo Transacao + funções auxiliares
├── requirements.txt    # Dependências (inclui groq==0.4.2, pillow)
├── .env.example        # Template de variáveis de ambiente
├── .gitignore          # Arquivos ignorados
├── services/
│   └── __init__.py     # Pacote vazio
└── utils/
    └── __init__.py     # Pacote vazio
```

### Dependências já instaladas
- `groq==0.4.2` - Cliente Python oficial da Groq
- `pillow==10.1.0` - Manipulação de imagens

### Configurações disponíveis (config.py)
```python
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = 'llama-3.2-90b-vision-preview'
CATEGORIAS_DESPESA = ['Hortifruti', 'Açougue', 'Bebidas', 'Embalagens', 'Limpeza', 'Manutenção', 'Outros']
```

---

## 🎯 REQUISITOS TÉCNICOS

### 1. Criar `services/groq_service.py`
**Critério de aceite**: Arquivo contém classe `GroqService` funcional

```python
# Estrutura obrigatória:

import base64
import json
import logging
from groq import Groq
from config import Config

logger = logging.getLogger(__name__)

class GroqService:
    """Serviço de integração com Groq para OCR de notas fiscais."""
    
    def __init__(self):
        """Inicializa cliente Groq com API key do config."""
        pass
    
    def processar_nota(self, imagem_base64: str) -> dict:
        """
        Processa imagem de nota fiscal e extrai dados estruturados.
        
        Args:
            imagem_base64: String base64 da imagem (com ou sem prefixo data:image)
        
        Returns:
            dict: {
                'sucesso': bool,
                'dados': {
                    'data': 'YYYY-MM-DD',
                    'estabelecimento': 'Nome do Fornecedor',
                    'valor_total': 123.45,
                    'categoria': 'Hortifruti'
                }
            }
            OU em caso de erro:
            {
                'sucesso': False,
                'erro': 'Mensagem descritiva do erro'
            }
        """
        pass
    
    def _preparar_imagem(self, imagem_base64: str) -> str:
        """Remove prefixo data:image se existir e valida base64."""
        pass
    
    def _construir_prompt(self) -> str:
        """Retorna o prompt do sistema para extração de dados."""
        pass
    
    def _validar_resposta(self, dados: dict) -> bool:
        """Valida se a resposta da IA contém todos os campos obrigatórios."""
        pass
    
    def _normalizar_categoria(self, categoria: str) -> str:
        """Normaliza categoria para uma das válidas ou retorna 'Outros'."""
        pass


# Singleton para reutilização
_groq_service = None

def get_groq_service() -> GroqService:
    """Retorna instância singleton do serviço Groq."""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
```

---

### 2. Implementar o Prompt de OCR
**Critério de aceite**: Prompt otimizado para extração precisa de dados

```python
PROMPT_SISTEMA = """
Você é um assistente contábil especializado em restaurantes.
Analise esta imagem de nota fiscal ou recibo e extraia os dados.

INSTRUÇÕES:
1. Identifique a data da compra (formato: YYYY-MM-DD)
2. Identifique o nome do estabelecimento/fornecedor
3. Extraia o valor TOTAL da nota (apenas números, sem R$)
4. Classifique a compra em UMA categoria:
   - Hortifruti: legumes, verduras, frutas
   - Açougue: carnes, aves, peixes
   - Bebidas: refrigerantes, sucos, cervejas
   - Embalagens: marmitex, sacolas, guardanapos
   - Limpeza: produtos de limpeza
   - Manutenção: reparos, peças, serviços
   - Outros: qualquer item não listado

RESPONDA APENAS COM JSON VÁLIDO:
{
    "data": "YYYY-MM-DD",
    "estabelecimento": "Nome do Fornecedor",
    "valor_total": 123.45,
    "categoria": "Categoria"
}

Se a imagem não for legível ou não for uma nota fiscal, retorne:
{"erro": "Descrição do problema"}
"""
```

---

### 3. Implementar validações robustas
**Critério de aceite**: Todas as validações funcionando

```python
def _validar_resposta(self, dados: dict) -> bool:
    """
    Validações obrigatórias:
    1. Campos 'data', 'valor_total', 'categoria' existem
    2. Data está no formato YYYY-MM-DD válido
    3. valor_total é número positivo
    4. categoria é uma das válidas (ou normaliza para 'Outros')
    """
    pass
```

---

### 4. Implementar tratamento de erros
**Critério de aceite**: Erros são tratados graciosamente

| Cenário | Tratamento |
|---------|------------|
| API key inválida | Logar erro, retornar mensagem amigável |
| Timeout da API | Retry 1x, depois retornar erro |
| Imagem ilegível | Retornar erro sugerindo melhorar foto |
| JSON inválido na resposta | Tentar extrair JSON do texto, se falhar retornar erro |
| Categoria não reconhecida | Normalizar para 'Outros' |

---

### 5. Criar `utils/helpers.py` com funções auxiliares
**Critério de aceite**: Funções de suporte implementadas

```python
def extrair_json_de_texto(texto: str) -> dict:
    """
    Extrai JSON de texto que pode conter markdown ou texto adicional.
    Procura por {} e tenta parsear como JSON.
    """
    pass

def validar_data(data_str: str) -> bool:
    """Valida se string está no formato YYYY-MM-DD válido."""
    pass

def formatar_valor(valor: any) -> float:
    """Converte valor para float, tratando strings com vírgula/R$."""
    pass
```

---

## 📐 PADRÕES A SEGUIR

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# Níveis de log:
logger.debug("Detalhes internos")      # Desenvolvimento
logger.info("Operações normais")        # Produção
logger.warning("Situações inesperadas") # Atenção
logger.error("Erros que precisam ação") # Crítico
```

### Tratamento de Exceções
```python
try:
    resposta = self.client.chat.completions.create(...)
except Exception as e:
    logger.error(f"Erro ao chamar Groq API: {e}")
    return {
        'sucesso': False,
        'erro': 'Serviço de IA temporariamente indisponível. Tente novamente.'
    }
```

### Chamada à API Groq (Vision)
```python
from groq import Groq

client = Groq(api_key=Config.GROQ_API_KEY)

response = client.chat.completions.create(
    model=Config.GROQ_MODEL,  # 'llama-3.2-90b-vision-preview'
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": self._construir_prompt()
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{imagem_base64}"
                    }
                }
            ]
        }
    ],
    temperature=0.1,  # Baixa para respostas mais determinísticas
    max_tokens=500
)

texto_resposta = response.choices[0].message.content
```

---

## 🚫 NÃO FAZER

1. ❌ **NÃO** criar rotas Flask (será na Fase 3)
2. ❌ **NÃO** criar templates HTML (será na Fase 4)
3. ❌ **NÃO** salvar no banco de dados (será na Fase 3)
4. ❌ **NÃO** hardcodar a API key - usar Config.GROQ_API_KEY
5. ❌ **NÃO** usar `print()` - usar `logging`
6. ❌ **NÃO** ignorar erros - sempre tratar e retornar mensagem clara
7. ❌ **NÃO** confiar cegamente na IA - validar todos os campos

---

## 📦 ENTREGÁVEIS

| # | Arquivo | Descrição |
|---|---------|-----------|
| 1 | `services/groq_service.py` | Serviço completo de OCR com Groq |
| 2 | `utils/helpers.py` | Funções auxiliares de validação |

---

## ✅ VERIFICAÇÃO

### 1. Teste de importação
```bash
cd MONA_Controle_financeiro
python -c "from services.groq_service import get_groq_service; print('Import OK')"
```

### 2. Teste unitário básico (criar arquivo temporário)
```python
# test_groq.py (arquivo de teste temporário)
from services.groq_service import get_groq_service

# Teste 1: Inicialização
service = get_groq_service()
print(f"✅ Serviço inicializado: {service}")

# Teste 2: Validação de categoria
categoria = service._normalizar_categoria("legumes")
assert categoria == "Hortifruti", f"Esperado 'Hortifruti', obtido '{categoria}'"
print("✅ Normalização de categoria OK")

# Teste 3: Validação de resposta
dados_validos = {
    "data": "2025-12-26",
    "estabelecimento": "CEASA",
    "valor_total": 150.00,
    "categoria": "Hortifruti"
}
assert service._validar_resposta(dados_validos) == True
print("✅ Validação de resposta OK")

# Teste 4: Com imagem real (requer API key configurada)
# Descomentar apenas se tiver .env configurado:
# import base64
# with open("nota_teste.jpg", "rb") as f:
#     img_base64 = base64.b64encode(f.read()).decode()
# resultado = service.processar_nota(img_base64)
# print(f"Resultado OCR: {resultado}")
```

### 3. Executar teste
```bash
python test_groq.py
```

### 4. Resultado esperado
```
✅ Serviço inicializado: <services.groq_service.GroqService object>
✅ Normalização de categoria OK
✅ Validação de resposta OK
```

---

## 📝 NOTAS ADICIONAIS

### Sobre o modelo Groq Vision
- `llama-3.2-90b-vision-preview` é o modelo mais preciso para OCR
- Alternativa mais rápida: `llama-3.2-11b-vision-preview`
- Limite de imagem: ~4MB (comprimir se necessário)

### Sobre o formato base64
```python
# Frontend envia: "data:image/jpeg;base64,/9j/4AAQ..."
# API Groq espera: apenas a parte base64 sem prefixo
# Função _preparar_imagem() deve tratar isso
```

### Categorias aceitas
Exatamente estas 7, case-sensitive:
```python
['Hortifruti', 'Açougue', 'Bebidas', 'Embalagens', 'Limpeza', 'Manutenção', 'Outros']
```

---

> **Próxima fase**: Fase 3 - Backend Flask (Rotas API)
