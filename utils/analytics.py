"""
Módulo de Análise de Dados - GestorBot

Este módulo fornece funções para análise de padrões de compra,
incluindo fornecedores mais utilizados, palavras-chave recorrentes
e geração de insights automáticos.
"""

import logging
import re
from collections import Counter
from typing import Optional

logger = logging.getLogger(__name__)

# Palavras comuns a serem ignoradas na análise
STOP_WORDS = {
    'de', 'da', 'do', 'das', 'dos', 'e', 'em', 'na', 'no', 'nas', 'nos',
    'para', 'por', 'com', 'sem', 'um', 'uma', 'uns', 'umas', 'o', 'a',
    'os', 'as', 'que', 'se', 'ao', 'aos', 'pag', 'pagamento', 'pago',
    'compra', 'compras', 'nota', 'fiscal', 'nf', 'cf', 'cupom', 'ref',
    'lote', 'lt', 'kg', 'un', 'pc', 'cx', 'pct', 'ml', 'gramas', 'unidade'
}

# Tamanho mínimo de palavra para considerar
MIN_WORD_LENGTH = 3


def get_top_fornecedores(transacoes: list, limite: int = 10) -> list:
    """
    Retorna os fornecedores mais utilizados com base nas transações.
    
    Args:
        transacoes: Lista de objetos Transacao
        limite: Quantidade máxima de fornecedores no ranking
    
    Returns:
        list: Lista de dicts [{'nome': 'Fornecedor', 'quantidade': 15, 'valor_total': 5000.0}, ...]
    """
    try:
        fornecedores = {}
        
        for t in transacoes:
            if not t.estabelecimento or t.estabelecimento.strip() == '':
                continue
            
            nome = t.estabelecimento.strip().upper()
            
            if nome not in fornecedores:
                fornecedores[nome] = {'quantidade': 0, 'valor_total': 0.0}
            
            fornecedores[nome]['quantidade'] += 1
            fornecedores[nome]['valor_total'] += t.valor
        
        # Ordena por quantidade (mais frequente primeiro)
        ranking = sorted(
            [{'nome': k, **v} for k, v in fornecedores.items()],
            key=lambda x: x['quantidade'],
            reverse=True
        )[:limite]
        
        logger.info(f"Top {limite} fornecedores calculados: {len(ranking)} resultados")
        return ranking
        
    except Exception as e:
        logger.error(f"Erro ao calcular top fornecedores: {e}")
        return []


def extrair_palavras_chave(transacoes: list, limite: int = 15) -> list:
    """
    Extrai palavras-chave mais frequentes das descrições das transações.
    
    Args:
        transacoes: Lista de objetos Transacao
        limite: Quantidade máxima de palavras no ranking
    
    Returns:
        list: Lista de dicts [{'palavra': 'CERVEJA', 'frequencia': 45}, ...]
    """
    try:
        todas_palavras = []
        
        for t in transacoes:
            # Combina descrição e estabelecimento
            texto = f"{t.descricao or ''} {t.estabelecimento or ''}"
            
            # Remove caracteres especiais e divide em palavras
            palavras = re.findall(r'[a-záàâãéèêíìîóòôõúùûç]+', texto.lower())
            
            # Filtra palavras curtas e stop words
            palavras_filtradas = [
                p.upper() for p in palavras 
                if len(p) >= MIN_WORD_LENGTH and p not in STOP_WORDS
            ]
            
            todas_palavras.extend(palavras_filtradas)
        
        # Conta frequência
        contador = Counter(todas_palavras)
        
        # Retorna as mais frequentes
        ranking = [
            {'palavra': palavra, 'frequencia': freq}
            for palavra, freq in contador.most_common(limite)
        ]
        
        logger.info(f"Top {limite} palavras-chave extraídas")
        return ranking
        
    except Exception as e:
        logger.error(f"Erro ao extrair palavras-chave: {e}")
        return []


def gerar_insights(transacoes: list, totais: dict) -> list:
    """
    Gera insights automáticos sobre os padrões de compra.
    
    Args:
        transacoes: Lista de objetos Transacao (despesas)
        totais: Dict com {'receitas': X, 'despesas': Y, 'lucro': Z}
    
    Returns:
        list: Lista de strings com insights
    """
    try:
        insights = []
        
        if not transacoes or totais['despesas'] == 0:
            return ['📊 Sem dados suficientes para gerar insights']
        
        # 1. Fornecedor principal
        fornecedores = get_top_fornecedores(transacoes, limite=1)
        if fornecedores:
            top = fornecedores[0]
            percentual = (top['valor_total'] / totais['despesas']) * 100
            insights.append(
                f"🏪 <strong>{top['nome']}</strong> é o principal fornecedor, "
                f"representando <strong>{percentual:.1f}%</strong> das despesas "
                f"({top['quantidade']} compras)"
            )
        
        # 2. Categoria mais cara
        categorias = {}
        for t in transacoes:
            cat = t.categoria or 'Outros'
            categorias[cat] = categorias.get(cat, 0) + t.valor
        
        if categorias:
            cat_top = max(categorias.items(), key=lambda x: x[1])
            percentual_cat = (cat_top[1] / totais['despesas']) * 100
            insights.append(
                f"📊 A categoria <strong>{cat_top[0]}</strong> representa "
                f"<strong>{percentual_cat:.1f}%</strong> do total de despesas"
            )
        
        # 3. Ticket médio
        if transacoes:
            ticket_medio = totais['despesas'] / len(transacoes)
            insights.append(
                f"🧾 Ticket médio por compra: <strong>R$ {ticket_medio:.2f}</strong>"
            )
        
        # 4. Compra mais cara
        if transacoes:
            maior_compra = max(transacoes, key=lambda t: t.valor)
            insights.append(
                f"💰 Maior compra: <strong>R$ {maior_compra.valor:.2f}</strong> "
                f"em {maior_compra.estabelecimento or 'N/A'}"
            )
        
        # 5. Lucratividade
        if totais['lucro'] > 0:
            margem = (totais['lucro'] / totais['receitas']) * 100 if totais['receitas'] > 0 else 0
            insights.append(
                f"✅ Margem de lucro de <strong>{margem:.1f}%</strong> no período"
            )
        elif totais['lucro'] < 0:
            insights.append(
                f"⚠️ <span class='text-danger'>Prejuízo de R$ {abs(totais['lucro']):.2f}</span> no período"
            )
        
        logger.info(f"Gerados {len(insights)} insights")
        return insights
        
    except Exception as e:
        logger.error(f"Erro ao gerar insights: {e}")
        return ['❌ Erro ao gerar insights']


def get_analise_completa(transacoes_despesas: list, totais: dict) -> dict:
    """
    Retorna análise completa para o dashboard.
    
    Args:
        transacoes_despesas: Lista de transações de despesas
        totais: Dict com totais do período
    
    Returns:
        dict: {
            'fornecedores': [...],
            'palavras_chave': [...],
            'insights': [...]
        }
    """
    return {
        'fornecedores': get_top_fornecedores(transacoes_despesas, limite=10),
        'palavras_chave': extrair_palavras_chave(transacoes_despesas, limite=15),
        'insights': gerar_insights(transacoes_despesas, totais)
    }
