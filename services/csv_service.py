"""
Serviço para exportação de transações em formato CSV.
"""

import csv
import io
from datetime import datetime
from typing import List
import logging

logger = logging.getLogger(__name__)


def gerar_csv_transacoes(transacoes: List, mes: int, ano: int) -> bytes:
    """
    Gera arquivo CSV com as transações do mês.
    
    Args:
        transacoes: Lista de objetos Transacao
        mes: Mês do relatório
        ano: Ano do relatório
    
    Returns:
        bytes: Conteúdo do arquivo CSV em bytes (UTF-8 com BOM para Excel)
    """
    
    # Buffer de string
    output = io.StringIO()
    
    # Cabeçalhos
    fieldnames = [
        'Data',
        'Tipo',
        'Categoria',
        'Subcategoria',
        'Descrição',
        'Estabelecimento',
        'Valor',
        'Status'
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    
    # Dados
    for t in transacoes:
        writer.writerow({
            'Data': t.data.strftime('%d/%m/%Y') if t.data else '',
            'Tipo': t.tipo or '',
            'Categoria': t.categoria or '',
            'Subcategoria': t.subcategoria or '',
            'Descrição': t.descricao or '',
            'Estabelecimento': t.estabelecimento or '',
            'Valor': str(t.valor).replace('.', ',') if t.valor else '0,00',
            'Status': t.status or 'CONFIRMADO'
        })
    
    # Retorna bytes com BOM para Excel reconhecer UTF-8
    csv_content = output.getvalue()
    return ('\ufeff' + csv_content).encode('utf-8')


def gerar_csv_resumo(totais: dict, gastos_categoria: dict, receitas_categoria: dict, mes: int, ano: int) -> bytes:
    """
    Gera arquivo CSV com resumo financeiro do mês.
    
    Args:
        totais: Dicionário com receitas, despesas e lucro
        gastos_categoria: Dicionário de gastos por categoria
        receitas_categoria: Dicionário de receitas por categoria
        mes: Mês do relatório
        ano: Ano do relatório
    
    Returns:
        bytes: Conteúdo do arquivo CSV em bytes
    """
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # Título
    meses = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mes_nome = meses[mes] if 1 <= mes <= 12 else 'Mês'
    
    writer.writerow(['MONA Beach Club - Resumo Financeiro'])
    writer.writerow([f'{mes_nome} de {ano}'])
    writer.writerow([])
    
    # Resumo
    writer.writerow(['RESUMO FINANCEIRO'])
    writer.writerow(['Descrição', 'Valor'])
    writer.writerow(['Receitas', str(totais.get('receitas', 0)).replace('.', ',')])
    writer.writerow(['Despesas', str(totais.get('despesas', 0)).replace('.', ',')])
    writer.writerow(['Lucro', str(totais.get('lucro', 0)).replace('.', ',')])
    writer.writerow([])
    
    # Despesas por categoria
    writer.writerow(['DESPESAS POR CATEGORIA'])
    writer.writerow(['Categoria', 'Valor', 'Percentual'])
    total_desp = sum(gastos_categoria.values()) if gastos_categoria else 1
    for cat, val in sorted(gastos_categoria.items(), key=lambda x: x[1], reverse=True):
        pct = (val / total_desp * 100) if total_desp > 0 else 0
        writer.writerow([cat, str(val).replace('.', ','), f'{pct:.1f}%'])
    writer.writerow([])
    
    # Receitas por categoria
    writer.writerow(['RECEITAS POR CATEGORIA'])
    writer.writerow(['Categoria', 'Valor', 'Percentual'])
    total_rec = sum(receitas_categoria.values()) if receitas_categoria else 1
    for cat, val in sorted(receitas_categoria.items(), key=lambda x: x[1], reverse=True):
        pct = (val / total_rec * 100) if total_rec > 0 else 0
        writer.writerow([cat, str(val).replace('.', ','), f'{pct:.1f}%'])
    
    # Retorna bytes com BOM
    csv_content = output.getvalue()
    return ('\ufeff' + csv_content).encode('utf-8')
