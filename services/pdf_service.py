"""
Servico para geracao de relatorios PDF do GestorBot.
Versao usando arquivo temporario para garantir escrita correta.
"""

from fpdf import FPDF
from datetime import datetime
from typing import List, Dict
import logging
import tempfile
import os
import matplotlib
matplotlib.use('Agg')  # Backend sem GUI
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# Cores (RGB)
VERDE = (40, 167, 69)
VERMELHO = (220, 53, 69)
CINZA = (128, 128, 128)
PRETO = (0, 0, 0)
AZUL = (13, 110, 253)

MESES = ['', 'Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def remover_acentos(texto):
    """Remove acentos de uma string."""
    if texto is None:
        return ''
    texto = str(texto)
    acentos = {
        '\xe1': 'a', '\xe0': 'a', '\xe3': 'a', '\xe2': 'a', '\xe4': 'a',
        '\xe9': 'e', '\xe8': 'e', '\xea': 'e', '\xeb': 'e',
        '\xed': 'i', '\xec': 'i', '\xee': 'i', '\xef': 'i',
        '\xf3': 'o', '\xf2': 'o', '\xf5': 'o', '\xf4': 'o', '\xf6': 'o',
        '\xfa': 'u', '\xf9': 'u', '\xfb': 'u', '\xfc': 'u',
        '\xe7': 'c', '\xf1': 'n',
        '\xc1': 'A', '\xc0': 'A', '\xc3': 'A', '\xc2': 'A', '\xc4': 'A',
        '\xc9': 'E', '\xc8': 'E', '\xca': 'E', '\xcb': 'E',
        '\xcd': 'I', '\xcc': 'I', '\xce': 'I', '\xcf': 'I',
        '\xd3': 'O', '\xd2': 'O', '\xd5': 'O', '\xd4': 'O', '\xd6': 'O',
        '\xda': 'U', '\xd9': 'U', '\xdb': 'U', '\xdc': 'U',
        '\xc7': 'C', '\xd1': 'N',
    }
    resultado = []
    for char in texto:
        resultado.append(acentos.get(char, char))
    return ''.join(resultado)


def formatar_moeda(valor):
    """Formata valor para moeda brasileira."""
    try:
        valor = float(valor)
        formatted = "{:,.2f}".format(valor)
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return "R$ " + formatted
    except:
        return "R$ 0,00"


def gerar_grafico_rosca(gastos_categoria):
    """Gera gráfico em rosca das categorias de despesas."""
    if not gastos_categoria or len(gastos_categoria) == 0:
        return None
    
    # Prepara dados
    categorias = list(gastos_categoria.keys())
    valores = list(gastos_categoria.values())
    
    # Cores personalizadas para categorias
    cores = ['#28a745', '#17a2b8', '#8d6e63', '#455a64', '#651fff', 
             '#00bcd4', '#ff5722', '#ffc107', '#9c27b0', '#607d8b']
    
    # Cria figura
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='white')
    
    # Gráfico rosca (donut) com números FORA
    wedges, texts, autotexts = ax.pie(
        valores,
        labels=None,
        autopct='%1.1f%%',
        startangle=90,
        colors=cores[:len(categorias)],
        pctdistance=1.2,  # Porcentagens FORA da rosca
        wedgeprops=dict(width=0.5, edgecolor='white')
    )
    
    # Estilo dos textos de porcentagem - PRETO
    for autotext in autotexts:
        autotext.set_color('black')  # COR PRETA
        autotext.set_fontsize(8)
        autotext.set_weight('bold')
    
    # Adiciona legenda compacta fora do gráfico
    ax.legend(
        categorias,
        loc='center left',
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=7,
        frameon=False
    )
    
    ax.axis('equal')
    plt.tight_layout()
    
    # Salva em arquivo temporário
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return temp_file.name


class RelatorioPDF(FPDF):
    def __init__(self, mes, ano):
        super().__init__()
        self.mes = int(mes)
        self.ano = int(ano)
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(13, 110, 253)
        self.cell(0, 10, 'MONA Beach Club', align='C', ln=True)
        
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'Relatorio Financeiro', align='C', ln=True)
        
        self.set_font('Helvetica', '', 12)
        self.set_text_color(128, 128, 128)
        mes_nome = MESES[self.mes] if 1 <= self.mes <= 12 else 'Mes'
        self.cell(0, 8, mes_nome + " de " + str(self.ano), align='C', ln=True)
        
        self.ln(3)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)
        self.set_text_color(0, 0, 0)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Gerado em ' + datetime.now().strftime('%d/%m/%Y %H:%M') + 
                  ' | Pagina ' + str(self.page_no()), align='C')


def gerar_relatorio_mensal(mes, ano, totais, gastos_categoria, receitas_categoria, transacoes, tipo_filtro=''):
    """Gera relatorio PDF mensal. Retorna bytes. tipo_filtro pode ser 'DESPESA', 'RECEITA' ou vazio."""
    
    pdf = RelatorioPDF(mes, ano)
    pdf.add_page()
    
    # === RESUMO FINANCEIRO COM GRÁFICO ===
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'RESUMO FINANCEIRO', ln=True)
    pdf.ln(3)
    
    # Gera e insere gráfico rosca ao lado do resumo
    grafico_path = None
    if gastos_categoria and len(gastos_categoria) > 0:
        try:
            grafico_path = gerar_grafico_rosca(gastos_categoria)
            if grafico_path:
                # Salva posição atual
                y_inicial = pdf.get_y()
                # Gráfico mais à ESQUERDA (90) e mais ACIMA (25mm)
                pdf.image(grafico_path, x=90, y=y_inicial - 25, w=60)
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico: {e}")
    
    # Resumo financeiro à esquerda
    pdf.set_font('Helvetica', '', 11)
    
    receitas = float(totais.get('receitas', 0)) if totais else 0
    despesas = float(totais.get('despesas', 0)) if totais else 0
    lucro = float(totais.get('lucro', 0)) if totais else 0
    
    pdf.set_text_color(40, 167, 69)
    pdf.cell(50, 8, 'Receitas:')
    pdf.cell(0, 8, formatar_moeda(receitas), ln=True)
    
    pdf.set_text_color(220, 53, 69)
    pdf.cell(50, 8, 'Despesas:')
    pdf.cell(0, 8, formatar_moeda(despesas), ln=True)
    
    if lucro >= 0:
        pdf.set_text_color(40, 167, 69)
    else:
        pdf.set_text_color(220, 53, 69)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(50, 8, 'Lucro:')
    pdf.cell(0, 8, formatar_moeda(lucro), ln=True)
    
    pdf.set_text_color(0, 0, 0)
    
    # Remove arquivo temporário do gráfico
    if grafico_path:
        try:
            os.unlink(grafico_path)
        except:
            pass
    
    pdf.ln(8)
    
    # === DESPESAS POR CATEGORIA ===
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'DESPESAS POR CATEGORIA', ln=True)
    pdf.ln(2)
    
    if gastos_categoria:
        pdf.set_font('Helvetica', '', 10)
        total = sum(gastos_categoria.values()) or 1
        for cat, val in sorted(gastos_categoria.items(), key=lambda x: x[1], reverse=True):
            pct = (val / total * 100)
            pdf.set_text_color(220, 53, 69)
            pdf.cell(70, 7, "  " + remover_acentos(str(cat)))
            pdf.cell(40, 7, formatar_moeda(val))
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 7, "(" + "{:.1f}".format(pct) + "%)", ln=True)
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 7, 'Nenhuma despesa neste periodo.', ln=True)
    
    pdf.ln(8)
    
    # === RECEITAS POR CATEGORIA ===
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'RECEITAS POR CATEGORIA', ln=True)
    pdf.ln(2)
    
    if receitas_categoria:
        pdf.set_font('Helvetica', '', 10)
        total = sum(receitas_categoria.values()) or 1
        for cat, val in sorted(receitas_categoria.items(), key=lambda x: x[1], reverse=True):
            pct = (val / total * 100)
            pdf.set_text_color(40, 167, 69)
            pdf.cell(70, 7, "  " + remover_acentos(str(cat)))
            pdf.cell(40, 7, formatar_moeda(val))
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 7, "(" + "{:.1f}".format(pct) + "%)", ln=True)
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 7, 'Nenhuma receita neste periodo.', ln=True)
    
    pdf.ln(8)
    
    # === TRANSACOES ===
    if pdf.get_y() > 200:
        pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'TRANSACOES', ln=True)
    pdf.ln(2)
    
    if transacoes and len(transacoes) > 0:
        # Cabecalho
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(20, 8, 'Data', border=1, fill=True)
        pdf.cell(12, 8, 'Tipo', border=1, fill=True)
        pdf.cell(45, 8, 'Descricao', border=1, fill=True)
        pdf.cell(30, 8, 'Categoria', border=1, fill=True)
        pdf.cell(30, 8, 'Subcategoria', border=1, fill=True)
        pdf.cell(0, 8, 'Valor', border=1, fill=True, ln=True)
        
        pdf.set_font('Helvetica', '', 8)
        for t in transacoes:
            if pdf.get_y() > 260:
                pdf.add_page()
                pdf.set_font('Helvetica', 'B', 8)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(20, 8, 'Data', border=1, fill=True)
                pdf.cell(12, 8, 'Tipo', border=1, fill=True)
                pdf.cell(45, 8, 'Descricao', border=1, fill=True)
                pdf.cell(30, 8, 'Categoria', border=1, fill=True)
                pdf.cell(30, 8, 'Subcategoria', border=1, fill=True)
                pdf.cell(0, 8, 'Valor', border=1, fill=True, ln=True)
                pdf.set_font('Helvetica', '', 8)
            
            # Dados da transacao
            data_fmt = t.data.strftime('%d/%m/%Y') if hasattr(t, 'data') and t.data else '-'
            desc = remover_acentos(str(getattr(t, 'descricao', '') or getattr(t, 'estabelecimento', '') or '-'))
            cat = remover_acentos(str(getattr(t, 'categoria', '-') or '-'))
            subcat = remover_acentos(str(getattr(t, 'subcategoria', '-') or '-'))
            obs = remover_acentos(str(getattr(t, 'observacao', '') or ''))
            tipo = getattr(t, 'tipo', 'DESPESA')
            valor = float(getattr(t, 'valor', 0))
            
            if tipo == 'RECEITA':
                pdf.set_text_color(40, 167, 69)
                tipo_txt = 'REC'
            else:
                pdf.set_text_color(220, 53, 69)
                tipo_txt = 'DES'
            
            # Linha principal da transação
            pdf.cell(20, 7, data_fmt, border=1)
            pdf.cell(12, 7, tipo_txt, border=1)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(45, 7, desc[:22], border=1)
            pdf.cell(30, 7, cat[:12], border=1)
            pdf.cell(30, 7, subcat[:12], border=1)
            if tipo == 'RECEITA':
                pdf.set_text_color(40, 167, 69)
            else:
                pdf.set_text_color(220, 53, 69)
            pdf.cell(0, 7, formatar_moeda(valor), border=1, ln=True)
            pdf.set_text_color(0, 0, 0)
            
            # Se houver observação, adiciona em linha extra com multi_cell
            if obs and len(obs) > 0:
                pdf.set_font('Helvetica', 'I', 7)
                pdf.set_text_color(100, 100, 100)
                # Cell vazia para alinhar com descrição
                pdf.cell(32, 0, '', border=0)
                # Multi_cell para quebra automática de texto
                x_before = pdf.get_x()
                y_before = pdf.get_y()
                pdf.multi_cell(0, 4, 'Obs: ' + obs, border=0)
                pdf.set_font('Helvetica', '', 8)
                pdf.set_text_color(0, 0, 0)
        
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 7, "Total: " + str(len(transacoes)) + " transacoes", ln=True)
    else:
        pdf.set_font('Helvetica', 'I', 10)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(0, 7, 'Nenhuma transacao neste periodo.', ln=True)
    
    # Salvar em arquivo temporario e ler como bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp_path = tmp.name
    
    try:
        pdf.output(tmp_path)
        with open(tmp_path, 'rb') as f:
            pdf_bytes = f.read()
        return pdf_bytes
    finally:
        # Limpar arquivo temporario
        try:
            os.unlink(tmp_path)
        except:
            pass
