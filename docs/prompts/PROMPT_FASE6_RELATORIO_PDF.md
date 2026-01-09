# 📄 Fase 6: Relatório Automático PDF

> **Objetivo**: Implementar a geração de relatórios mensais em PDF com resumo financeiro, totais por categoria e lista de transações.

---

## 🎭 ROLE

Você é um **Desenvolvedor Python Sênior** especializado em:
- Geração de documentos PDF com FPDF2
- Formatação profissional de relatórios
- Manipulação de datas e dados financeiros
- Integração Flask + arquivos para download

**Seu estilo de código:**
- Classes bem estruturadas para geração de PDF
- Formatação consistente de moeda brasileira
- Tratamento de edge cases (mês sem dados)
- Código reutilizável para futuros relatórios

---

## 📋 CONTEXTO

### Projeto
**GestorBot** é um sistema de gestão financeira para restaurantes com OCR inteligente de notas fiscais.

### O que já existe
```
MONA_Controle_financeiro/
├── config.py               # Configurações
├── models.py               # Transacao + funções auxiliares
├── app.py                  # Rotas Flask (incluindo /relatorio placeholder)
├── requirements.txt        # Inclui fpdf2==2.7.6
├── services/
│   ├── __init__.py
│   ├── groq_service.py     # OCR com Groq
│   └── pdf_service.py      # ← CRIAR AQUI
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── receita.html
│   └── dashboard.html
└── static/
    └── ...
```

### Dependência já instalada
```
fpdf2==2.7.6  # Biblioteca para geração de PDF
```

### Funções disponíveis (models.py)
```python
from models import get_transacoes_mes, get_totais_mes, get_gastos_por_categoria
```

---

## 🎯 REQUISITOS TÉCNICOS

### 1. Criar `services/pdf_service.py`
**Critério de aceite**: Serviço completo para geração de relatórios PDF

```python
"""
Serviço para geração de relatórios PDF do GestorBot.
"""

from fpdf import FPDF
from datetime import datetime
from typing import List, Dict
import os


class RelatorioPDF(FPDF):
    """Classe customizada para geração de relatórios financeiros."""
    
    def __init__(self, mes: int, ano: int):
        super().__init__()
        self.mes = mes
        self.ano = ano
        self.meses_nomes = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 
                           'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro',
                           'Outubro', 'Novembro', 'Dezembro']
    
    def header(self):
        """Cabeçalho de cada página."""
        # Logo ou título
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, 'GestorBot - Relatório Financeiro', align='C', ln=True)
        
        # Período
        self.set_font('Helvetica', '', 12)
        periodo = f"{self.meses_nomes[self.mes]} de {self.ano}"
        self.cell(0, 8, periodo, align='C', ln=True)
        
        # Linha separadora
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)
    
    def footer(self):
        """Rodapé de cada página."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        # Data de geração
        data_geracao = datetime.now().strftime('%d/%m/%Y às %H:%M')
        self.cell(0, 10, f'Gerado em {data_geracao} | Página {self.page_no()}', align='C')


def gerar_relatorio_mensal(
    mes: int, 
    ano: int, 
    totais: Dict, 
    gastos_categoria: Dict, 
    transacoes: List
) -> bytes:
    """
    Gera relatório PDF mensal.
    
    Args:
        mes: Mês do relatório (1-12)
        ano: Ano do relatório
        totais: Dict com {receitas, despesas, lucro}
        gastos_categoria: Dict com {categoria: valor}
        transacoes: Lista de transações do mês
    
    Returns:
        bytes: Conteúdo do PDF para download
    """
    pdf = RelatorioPDF(mes, ano)
    pdf.add_page()
    
    # Seção 1: Resumo Financeiro
    _adicionar_resumo(pdf, totais)
    
    # Seção 2: Gastos por Categoria
    _adicionar_gastos_categoria(pdf, gastos_categoria)
    
    # Seção 3: Lista de Transações
    _adicionar_lista_transacoes(pdf, transacoes)
    
    # Retornar como bytes
    return pdf.output()


def _adicionar_resumo(pdf: RelatorioPDF, totais: Dict):
    """Adiciona seção de resumo financeiro."""
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Resumo Financeiro', ln=True)
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 11)
    
    # Receitas
    pdf.set_text_color(40, 167, 69)  # Verde
    pdf.cell(60, 8, 'Receitas:', ln=False)
    pdf.cell(0, 8, f"R$ {totais['receitas']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), ln=True)
    
    # Despesas
    pdf.set_text_color(220, 53, 69)  # Vermelho
    pdf.cell(60, 8, 'Despesas:', ln=False)
    pdf.cell(0, 8, f"R$ {totais['despesas']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), ln=True)
    
    # Lucro
    cor_lucro = (40, 167, 69) if totais['lucro'] >= 0 else (220, 53, 69)
    pdf.set_text_color(*cor_lucro)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(60, 8, 'Lucro Líquido:', ln=False)
    pdf.cell(0, 8, f"R$ {totais['lucro']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), ln=True)
    
    pdf.set_text_color(0, 0, 0)  # Reset para preto
    pdf.ln(10)


def _adicionar_gastos_categoria(pdf: RelatorioPDF, gastos_categoria: Dict):
    """Adiciona seção de gastos por categoria."""
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Gastos por Categoria', ln=True)
    pdf.ln(2)
    
    if not gastos_categoria:
        pdf.set_font('Helvetica', 'I', 11)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 8, 'Nenhuma despesa registrada neste período.', ln=True)
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.set_font('Helvetica', '', 11)
        
        # Ordenar por valor (maior primeiro)
        gastos_ordenados = sorted(gastos_categoria.items(), key=lambda x: x[1], reverse=True)
        total_gastos = sum(gastos_categoria.values())
        
        for categoria, valor in gastos_ordenados:
            percentual = (valor / total_gastos * 100) if total_gastos > 0 else 0
            valor_fmt = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            pdf.cell(80, 7, f"• {categoria}", ln=False)
            pdf.cell(50, 7, valor_fmt, ln=False)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 7, f"({percentual:.1f}%)", ln=True)
            pdf.set_text_color(0, 0, 0)
    
    pdf.ln(10)


def _adicionar_lista_transacoes(pdf: RelatorioPDF, transacoes: List):
    """Adiciona tabela com lista de transações."""
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Detalhamento de Transações', ln=True)
    pdf.ln(2)
    
    if not transacoes:
        pdf.set_font('Helvetica', 'I', 11)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 8, 'Nenhuma transação neste período.', ln=True)
        return
    
    # Cabeçalho da tabela
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(25, 8, 'Data', border=1, fill=True)
    pdf.cell(20, 8, 'Tipo', border=1, fill=True)
    pdf.cell(70, 8, 'Descrição', border=1, fill=True)
    pdf.cell(35, 8, 'Categoria', border=1, fill=True)
    pdf.cell(40, 8, 'Valor', border=1, fill=True, ln=True)
    
    # Dados
    pdf.set_font('Helvetica', '', 9)
    for t in transacoes:
        # Verificar quebra de página
        if pdf.get_y() > 260:
            pdf.add_page()
            # Repetir cabeçalho
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(25, 8, 'Data', border=1, fill=True)
            pdf.cell(20, 8, 'Tipo', border=1, fill=True)
            pdf.cell(70, 8, 'Descrição', border=1, fill=True)
            pdf.cell(35, 8, 'Categoria', border=1, fill=True)
            pdf.cell(40, 8, 'Valor', border=1, fill=True, ln=True)
            pdf.set_font('Helvetica', '', 9)
        
        # Formatar dados
        data_fmt = t.data.strftime('%d/%m/%Y') if t.data else '-'
        descricao = (t.descricao or t.estabelecimento or '-')[:35]  # Truncar se necessário
        valor_fmt = f"R$ {t.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        # Cor conforme tipo
        if t.tipo == 'RECEITA':
            pdf.set_text_color(40, 167, 69)
        else:
            pdf.set_text_color(220, 53, 69)
        
        pdf.cell(25, 7, data_fmt, border=1)
        pdf.cell(20, 7, t.tipo[:3], border=1)  # DES ou REC
        pdf.set_text_color(0, 0, 0)
        pdf.cell(70, 7, descricao, border=1)
        pdf.cell(35, 7, t.categoria[:15], border=1)
        
        if t.tipo == 'RECEITA':
            pdf.set_text_color(40, 167, 69)
        else:
            pdf.set_text_color(220, 53, 69)
        pdf.cell(40, 7, valor_fmt, border=1, ln=True)
        pdf.set_text_color(0, 0, 0)
```

---

### 2. Atualizar rota `/relatorio` em `app.py`
**Critério de aceite**: Rota gera e retorna PDF para download

```python
from flask import send_file
from io import BytesIO
from services.pdf_service import gerar_relatorio_mensal

@app.route('/relatorio')
def gerar_relatorio():
    """
    Gera relatório mensal em PDF.
    
    Query Parameters:
        - mes: int (default: mês atual)
        - ano: int (default: ano atual)
    
    Response: Arquivo PDF para download
    """
    # Obter mês/ano
    hoje = date.today()
    mes = request.args.get('mes', hoje.month, type=int)
    ano = request.args.get('ano', hoje.year, type=int)
    
    # Validar
    if mes < 1 or mes > 12:
        mes = hoje.month
    
    try:
        # Buscar dados
        totais = get_totais_mes(ano, mes)
        gastos_cat = get_gastos_por_categoria(ano, mes)
        transacoes = get_transacoes_mes(ano, mes)
        
        # Ordenar transações por data
        transacoes_ordenadas = sorted(transacoes, key=lambda t: t.data)
        
        # Gerar PDF
        pdf_bytes = gerar_relatorio_mensal(
            mes=mes,
            ano=ano,
            totais=totais,
            gastos_categoria=gastos_cat,
            transacoes=transacoes_ordenadas
        )
        
        # Nome do arquivo
        meses = ['', 'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
                 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        filename = f"relatorio_{meses[mes]}_{ano}.pdf"
        
        # Retornar para download
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        flash('Erro ao gerar relatório. Tente novamente.', 'danger')
        return redirect(url_for('dashboard', mes=mes, ano=ano))
```

---

### 3. Adicionar imports necessários em `app.py`
**Critério de aceite**: Todos os imports funcionando

```python
# Adicionar no topo do app.py
from io import BytesIO
from services.pdf_service import gerar_relatorio_mensal
```

---

## 📐 PADRÕES A SEGUIR

### Formatação de Moeda Brasileira
```python
# Converter de 1234.56 para "R$ 1.234,56"
def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
```

### Cores no PDF
```python
# Padrão de cores (RGB)
VERDE = (40, 167, 69)    # Receitas
VERMELHO = (220, 53, 69)  # Despesas
CINZA = (128, 128, 128)   # Textos secundários
PRETO = (0, 0, 0)         # Textos principais
```

### Nomes de Arquivos
```python
# Formato: relatorio_mes_ano.pdf
# Sem acentos, lowercase
"relatorio_dezembro_2025.pdf"
```

---

## 🚫 NÃO FAZER

1. ❌ **NÃO** usar fontes que precisam ser instaladas (usar Helvetica built-in)
2. ❌ **NÃO** gerar PDF com mais de 50 transações sem paginação
3. ❌ **NÃO** salvar PDF no disco do servidor - sempre retornar como bytes
4. ❌ **NÃO** expor erros técnicos ao usuário - usar flash messages
5. ❌ **NÃO** criar relatórios para meses futuros
6. ❌ **NÃO** incluir informações sensíveis (API keys, etc.) no PDF

---

## 📦 ENTREGÁVEIS

| # | Arquivo | Descrição |
|---|---------|-----------|
| 1 | `services/pdf_service.py` | Serviço completo de geração de PDF |
| 2 | `app.py` | Rota `/relatorio` atualizada |

---

## ✅ VERIFICAÇÃO

### 1. Testar import
```bash
cd MONA_Controle_financeiro
python -c "from services.pdf_service import gerar_relatorio_mensal; print('OK')"
```

### 2. Criar dados de teste
```bash
# Criar transações
curl -X POST http://localhost:5000/transacao \
  -H "Content-Type: application/json" \
  -d '{"tipo":"DESPESA","valor":250,"data":"2025-12-15","categoria":"Açougue","descricao":"Carnes para semana"}'

curl -X POST http://localhost:5000/transacao \
  -H "Content-Type: application/json" \
  -d '{"tipo":"DESPESA","valor":180,"data":"2025-12-18","categoria":"Hortifruti","descricao":"CEASA"}'

curl -X POST http://localhost:5000/transacao \
  -H "Content-Type: application/json" \
  -d '{"tipo":"RECEITA","valor":1500,"data":"2025-12-20","categoria":"Vendas","descricao":"Fechamento sexta"}'
```

### 3. Baixar relatório
- Acessar http://localhost:5000/relatorio?mes=12&ano=2025
- Verificar se PDF baixa automaticamente
- Abrir PDF e verificar:
  - ✅ Cabeçalho com mês/ano
  - ✅ Resumo com receitas, despesas, lucro
  - ✅ Gastos por categoria com percentuais
  - ✅ Tabela de transações
  - ✅ Rodapé com data de geração

### 4. Testar mês vazio
- Acessar http://localhost:5000/relatorio?mes=1&ano=2024
- Verificar se PDF é gerado mesmo sem dados
- Verificar mensagens de "Nenhuma transação"

---

## 📝 NOTAS ADICIONAIS

### Sobre FPDF2
- Biblioteca leve, sem dependências externas
- Suporta Unicode nativamente
- Documentação: https://py-pdf.github.io/fpdf2/

### Sobre tamanho do PDF
- A4 padrão: 210 x 297 mm
- Margens já incluídas no FPDF
- `get_y() > 260` para verificar fim da página

### Futuras melhorias (pós-MVP)
- Adicionar gráficos no PDF (requer matplotlib)
- Logo da empresa no cabeçalho
- Comparativo com mês anterior
- Exportar para Excel além de PDF

---

> **Próxima fase**: Fase 7 - Verificação e Testes Finais
