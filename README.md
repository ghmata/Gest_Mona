# 🍽️ GestorBot - Gestão Financeira para Restaurantes

Sistema inteligente para controle de despesas e receitas com OCR de notas fiscais.

![Flask](https://img.shields.io/badge/Flask-2.x-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Funcionalidades

- 📷 **OCR Inteligente**: Tire foto da nota fiscal e o sistema preenche automaticamente
- 💰 **Controle de Caixa**: Lance receitas (PIX, Cartão, Caixa, Transferência)
- 📊 **Dashboard**: Visualize métricas e gráficos em tempo real
- 📄 **Relatórios PDF**: Gere relatórios mensais automaticamente
- 🔍 **Busca Avançada**: Filtre por data, categoria, valor e descrição
- 📱 **Mobile-First**: Interface otimizada para celular

## 📋 Pré-requisitos

- Python 3.11+
- Conta na Groq (para OCR): https://console.groq.com/

## 🔧 Instalação

1. Clone ou copie o projeto

2. Crie ambiente virtual:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure variáveis de ambiente:
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```
   
5. Edite `.env` e adicione sua `GROQ_API_KEY`

## ▶️ Executando

```bash
python app.py
```

Acesse: http://localhost:5000

## 📱 Uso

### Nova Despesa
1. Clique em "Nova Despesa"
2. Tire foto da nota fiscal
3. Confira os dados extraídos
4. Confirme

### Fechar Caixa
1. Clique em "Fechar Caixa"
2. Selecione o tipo (PIX, Cartão, etc.)
3. Informe valor e data
4. Registre

### Dashboard
- Navegue entre meses (◀ ▶)
- Alterne entre abas: Despesas | Receitas | Histórico
- Use filtros avançados
- Baixe relatório PDF

## 🔌 API Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Página inicial |
| `GET` | `/dashboard` | Dashboard com métricas |
| `GET` | `/receita` | Formulário de receita |
| `POST` | `/transacao` | Criar transação |
| `GET` | `/transacoes` | Listar transações |
| `POST` | `/upload-nota` | Upload + OCR de nota |
| `GET` | `/relatorio` | Baixar PDF do mês |
| `DELETE` | `/transacao/{id}` | Excluir transação |

## 📁 Estrutura do Projeto

```
MONA_Controle_financeiro/
├── app.py              # Aplicação principal Flask
├── config.py           # Configurações
├── models.py           # Modelos SQLAlchemy
├── wsgi.py             # Ponto de entrada WSGI (produção)
├── requirements.txt    # Dependências
├── README.md           # Documentação
├── .env.example        # Template de variáveis
│
├── routes/             # Rotas Flask (blueprints)
├── services/           # Serviços (OCR Groq, PDF)
├── templates/          # Templates HTML
├── static/             # CSS, JS, uploads
├── utils/              # Funções auxiliares
├── tests/              # Testes automatizados
│
├── scripts/            # Scripts de administração
│   ├── criar_admin.py  # Cria usuário admin
│   └── popular_banco.py# Popula banco com dados demo
│
└── docs/               # Documentação de desenvolvimento
    └── prompts/        # Prompts usados no desenvolvimento
```

## 🏷️ Categorias

### Despesas
- Frutos do Mar, Carnes e Aves, Hortifruti
- Bebidas, Cervejas, Destilados, Vinhos
- Laticínios, Embalagens, Limpeza
- Manutenção, Gás, Outros

### Receitas
- Vendas, Caixa, PIX, Cartão, Transferência, Outros

## 🆘 Resolução de Problemas

| Problema | Solução |
|----------|---------|
| Erro de API Key | Verifique se `GROQ_API_KEY` está no `.env` |
| Foto não processa | Use foto clara e bem iluminada |
| PDF não gera | Reinicie o servidor |
| Gráfico não aparece | Verifique conexão com internet (Chart.js) |

## 🔒 Segurança

- Nunca commit o arquivo `.env`
- A `SECRET_KEY` é gerada automaticamente se não definida
- Uploads são salvos localmente em `static/uploads/`

## 📄 Licença

MIT License - Use livremente para fins comerciais ou pessoais.

## 👨‍💻 Desenvolvido para

**MONA Beach Club** - Sistema de controle financeiro personalizado.

---

> 💡 **Dica**: Para popular o banco com dados de teste, execute:
> ```bash
> python popular_banco.py
> ```
