"""
Blueprint para rotas de API JSON do GestorBot.

Este módulo contém as rotas:
- API de totais (GET /api/totais)
- API de subcategorias (GET /api/subcategorias/<categoria>)
- API de gastos por subcategoria (GET /api/gastos-subcategoria)
"""

import logging
from datetime import date

from flask import Blueprint, request, jsonify

from config import Config
from models import get_totais_mes, get_gastos_por_categoria, get_gastos_por_subcategoria, get_totais_diarios_mes

logger = logging.getLogger(__name__)

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/totais')
def api_totais():
    """
    API para obter totais do mês em formato JSON.
    
    Query Parameters:
        - mes: int (1-12)
        - ano: int (ex: 2025)
    """
    try:
        hoje = date.today()
        mes = request.args.get('mes', hoje.month, type=int)
        ano = request.args.get('ano', hoje.year, type=int)
        
        totais = get_totais_mes(ano, mes)
        gastos_categoria = get_gastos_por_categoria(ano, mes)
        
        return jsonify({
            'sucesso': True,
            'mes': mes,
            'ano': ano,
            'faturamento': totais['receitas'],
            'gastos': totais['despesas'],
            'lucro': totais['lucro'],
            'gastos_por_categoria': gastos_categoria
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na API de totais: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao calcular totais.'
        }), 500


@bp.route('/subcategorias')
@bp.route('/subcategorias/<categoria>')
def api_subcategorias(categoria: str = None):
    """
    API para obter subcategorias de uma categoria específica ou todas.
    
    Path Parameters:
        - categoria: Nome da categoria principal (opcional)
    
    Response JSON:
        {"sucesso": true, "categoria": "Insumos", "subcategorias": [...]}
    """
    try:
        if categoria:
            # Retorna subcategorias de uma categoria específica
            subcategorias = Config.CATEGORIAS_SUBCATEGORIAS.get(categoria, [])
            if not subcategorias:
                return jsonify({
                    'sucesso': False,
                    'erro': f'Categoria "{categoria}" não encontrada.'
                }), 404
            
            return jsonify({
                'sucesso': True,
                'categoria': categoria,
                'subcategorias': subcategorias
            }), 200
        else:
            # Retorna todas as categorias e subcategorias
            return jsonify({
                'sucesso': True,
                'categorias': Config.CATEGORIAS_SUBCATEGORIAS
            }), 200
        
    except Exception as e:
        logger.error(f"Erro na API de subcategorias: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao buscar subcategorias.'
        }), 500


@bp.route('/gastos-subcategoria')
def api_gastos_subcategoria():
    """
    API para obter gastos por subcategoria de uma categoria específica.
    
    Query Parameters:
        - mes: int (1-12)
        - ano: int (ex: 2025)
        - categoria: Nome da categoria principal
    
    Response JSON:
        {"sucesso": true, "categoria": "Insumos", "gastos_por_subcategoria": {...}}
    """
    try:
        hoje = date.today()
        mes = request.args.get('mes', hoje.month, type=int)
        ano = request.args.get('ano', hoje.year, type=int)
        categoria = request.args.get('categoria', '').strip()
        
        if not categoria:
            return jsonify({
                'sucesso': False,
                'erro': 'Parâmetro "categoria" é obrigatório.'
            }), 400
        
        if categoria not in Config.CATEGORIAS_SUBCATEGORIAS:
            return jsonify({
                'sucesso': False,
                'erro': f'Categoria "{categoria}" não encontrada.'
            }), 404
        
        gastos = get_gastos_por_subcategoria(ano, mes, categoria)
        
        return jsonify({
            'sucesso': True,
            'mes': mes,
            'ano': ano,
            'categoria': categoria,
            'gastos_por_subcategoria': gastos
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na API de gastos por subcategoria: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao buscar gastos por subcategoria.'
        }), 500


@bp.route('/dados-diarios')
def api_dados_diarios():
    """
    API para obter dados diários (evolução) do mês.
    
    Query Parameters:
        - mes: int
        - ano: int
        
    Response JSON:
        {
            "sucesso": true,
            "dias": [1, 2, ...],
            "receitas": [...],
            "despesas": [...]
        }
    """
    try:
        hoje = date.today()
        mes = request.args.get('mes', hoje.month, type=int)
        ano = request.args.get('ano', hoje.year, type=int)
        
        dados = get_totais_diarios_mes(ano, mes)
        
        return jsonify({
            'sucesso': True,
            'mes': mes,
            'ano': ano,
            'dias': dados['dias'],
            'receitas': dados['receitas'],
            'despesas': dados['despesas']
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na API de dados diários: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao buscar dados diários.'
        }), 500

