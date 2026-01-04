"""
Blueprint para rotas de transações do GestorBot.

Este módulo contém as rotas para:
- Criar transação
- Listar transações
- Excluir transação
"""

import logging
from datetime import datetime, date

from flask import Blueprint, request, jsonify

from config import Config
from models import db, Transacao, get_transacoes_mes
from utils.helpers import formatar_valor, validar_data

logger = logging.getLogger(__name__)

bp = Blueprint('transacoes', __name__)


@bp.route('/transacao', methods=['POST'])
def criar_transacao():
    """
    Salva uma nova transação confirmada pelo usuário.
    
    Request JSON:
        {"tipo": "DESPESA", "valor": 245.80, "data": "2025-12-26", ...}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'sucesso': False,
                'erro': 'Requisição inválida.'
            }), 400
        
        tipo = data.get('tipo', '').upper()
        valor = data.get('valor')
        data_str = data.get('data')
        categoria = data.get('categoria')
        descricao = data.get('descricao', '')
        estabelecimento = data.get('estabelecimento', '')
        comprovante_url = data.get('comprovante_url', '')
        
        # Validações
        if tipo not in ['DESPESA', 'RECEITA']:
            return jsonify({
                'sucesso': False,
                'erro': 'Campo "tipo" deve ser "DESPESA" ou "RECEITA".'
            }), 400
        
        if valor is None:
            return jsonify({
                'sucesso': False,
                'erro': 'Campo "valor" é obrigatório.'
            }), 400
        
        try:
            valor_float = formatar_valor(valor)
            if valor_float <= 0:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Campo "valor" deve ser positivo.'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'sucesso': False,
                'erro': 'Campo "valor" inválido.'
            }), 400
        
        if not data_str:
            return jsonify({
                'sucesso': False,
                'erro': 'Campo "data" é obrigatório.'
            }), 400
        
        if not validar_data(data_str):
            return jsonify({
                'sucesso': False,
                'erro': 'Campo "data" deve estar no formato YYYY-MM-DD.'
            }), 400
        
        data_transacao = datetime.strptime(data_str, '%Y-%m-%d')
        
        if not categoria:
            return jsonify({
                'sucesso': False,
                'erro': 'Campo "categoria" é obrigatório.'
            }), 400
        
        CATEGORIAS_RECEITA = ['Vendas', 'Caixa', 'PIX', 'Cartão', 'Transferência', 'Outros']
        categorias_validas = Config.CATEGORIAS_DESPESA if tipo == 'DESPESA' else CATEGORIAS_RECEITA
        
        if categoria not in categorias_validas:
            categoria_normalizada = None
            for cat in categorias_validas:
                if categoria.lower() == cat.lower():
                    categoria_normalizada = cat
                    break
            categoria = categoria_normalizada or 'Outros'
        
        transacao = Transacao(
            tipo=tipo,
            valor=valor_float,
            data=data_transacao,
            categoria=categoria,
            descricao=descricao[:200] if descricao else None,
            estabelecimento=estabelecimento[:100] if estabelecimento else None,
            comprovante_url=comprovante_url[:500] if comprovante_url else None,
            status='CONFIRMADO'
        )
        
        db.session.add(transacao)
        db.session.commit()
        
        logger.info(f"Transação criada: ID {transacao.id} - {tipo} R${valor_float:.2f}")
        
        return jsonify({
            'sucesso': True,
            'id': transacao.id,
            'mensagem': 'Transação registrada com sucesso!'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar transação: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro interno ao salvar transação.'
        }), 500


@bp.route('/transacoes')
def listar_transacoes():
    """Lista transações com filtros opcionais."""
    try:
        hoje = date.today()
        mes = request.args.get('mes', hoje.month, type=int)
        ano = request.args.get('ano', hoje.year, type=int)
        tipo_filtro = request.args.get('tipo', '').upper()
        categoria_filtro = request.args.get('categoria', '')
        
        if mes < 1 or mes > 12:
            mes = hoje.month
        if ano < 2000 or ano > 2100:
            ano = hoje.year
        
        transacoes = get_transacoes_mes(ano, mes)
        
        if tipo_filtro in ['DESPESA', 'RECEITA']:
            transacoes = [t for t in transacoes if t.tipo == tipo_filtro]
        
        if categoria_filtro:
            transacoes = [t for t in transacoes if t.categoria.lower() == categoria_filtro.lower()]
        
        return jsonify({
            'transacoes': [t.to_dict() for t in transacoes],
            'total': len(transacoes),
            'filtros': {
                'mes': mes,
                'ano': ano,
                'tipo': tipo_filtro or None,
                'categoria': categoria_filtro or None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar transações: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao buscar transações.'
        }), 500


@bp.route('/transacao/<int:id>', methods=['DELETE'])
def excluir_transacao(id: int):
    """
    Exclui uma transação pelo ID.
    Requer senha de segurança para confirmar exclusão.
    
    Request JSON:
        {"senha": "sua_senha_aqui"}
    """
    try:
        # Validar senha de segurança
        data = request.get_json() or {}
        senha = data.get('senha', '')
        
        if senha != Config.SENHA_EXCLUSAO:
            return jsonify({
                'sucesso': False,
                'erro': 'Senha incorreta.'
            }), 403
        
        transacao = Transacao.query.get(id)
        
        if not transacao:
            return jsonify({
                'sucesso': False,
                'erro': 'Transação não encontrada.'
            }), 404
        
        db.session.delete(transacao)
        db.session.commit()
        
        logger.info(f"Transação excluída: ID {id}")
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Transação excluída com sucesso!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao excluir transação: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao excluir transação.'
        }), 500


@bp.route('/transacao/<int:id>', methods=['PUT', 'PATCH'])
def editar_transacao(id: int):
    """
    Edita uma transação existente.
    
    Request JSON:
        {"categoria": "Insumos", "subcategoria": "Frutos do Mar", "valor": 150.00, ...}
    """
    try:
        transacao = Transacao.query.get(id)
        
        if not transacao:
            return jsonify({
                'sucesso': False,
                'erro': 'Transação não encontrada.'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'sucesso': False,
                'erro': 'Requisição inválida. Envie um JSON com os campos a atualizar.'
            }), 400
        
        campos_alterados = []
        
        # Atualizar categoria
        if 'categoria' in data:
            nova_categoria = data['categoria'].strip()[:50] if data['categoria'] else ''
            if nova_categoria and transacao.categoria != nova_categoria:
                transacao.categoria = nova_categoria
                campos_alterados.append('categoria')
        
        # Atualizar subcategoria
        if 'subcategoria' in data:
            nova_subcategoria = data['subcategoria'].strip()[:50] if data['subcategoria'] else ''
            if transacao.subcategoria != nova_subcategoria:
                transacao.subcategoria = nova_subcategoria if nova_subcategoria else None
                campos_alterados.append('subcategoria')
        
        # Atualizar descrição
        if 'descricao' in data:
            nova_descricao = data['descricao'].strip()[:200] if data['descricao'] else ''
            if transacao.descricao != nova_descricao:
                transacao.descricao = nova_descricao if nova_descricao else None
                campos_alterados.append('descricao')
        
        # Atualizar valor
        if 'valor' in data:
            try:
                novo_valor = formatar_valor(data['valor'])
                if novo_valor > 0 and transacao.valor != novo_valor:
                    transacao.valor = novo_valor
                    campos_alterados.append('valor')
            except (ValueError, TypeError):
                pass  # Ignora valor inválido
        
        # Atualizar data
        if 'data' in data:
            if validar_data(data['data']):
                nova_data = datetime.strptime(data['data'], '%Y-%m-%d')
                if transacao.data != nova_data:
                    transacao.data = nova_data
                    campos_alterados.append('data')
        
        # Atualizar estabelecimento
        if 'estabelecimento' in data:
            novo_estabelecimento = data['estabelecimento'].strip()[:100] if data['estabelecimento'] else ''
            if transacao.estabelecimento != novo_estabelecimento:
                transacao.estabelecimento = novo_estabelecimento if novo_estabelecimento else None
                campos_alterados.append('estabelecimento')
        
        if not campos_alterados:
            return jsonify({
                'sucesso': True,
                'mensagem': 'Nenhuma alteração detectada.',
                'transacao': transacao.to_dict()
            }), 200
        
        db.session.commit()
        
        logger.info(f"Transação {id} editada. Campos: {', '.join(campos_alterados)}")
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Transação atualizada! Campos: {", ".join(campos_alterados)}',
            'transacao': transacao.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao editar transação {id}: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao editar transação.'
        }), 500
