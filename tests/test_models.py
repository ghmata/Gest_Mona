"""
Testes para modelos de dados do models.py.

Testa:
- Transacao: Criação, validação, conversão para dict
- Funções de consulta: get_transacoes_mes, get_totais_mes
"""

import pytest
from datetime import datetime, date
from models import db, Transacao, get_transacoes_mes, get_totais_mes


# =============================================================================
# TESTES: Modelo Transacao
# =============================================================================

class TestTransacao:
    """Testes para o modelo Transacao."""
    
    def test_criar_transacao_despesa(self, app):
        """Testa criação de transação de despesa."""
        with app.app_context():
            t = Transacao(
                tipo='DESPESA',
                valor=100.0,
                categoria='Hortifruti',
                descricao='Compra de verduras',
                data=date(2025, 12, 26)
            )
            db.session.add(t)
            db.session.commit()
            
            assert t.id is not None
            assert t.tipo == 'DESPESA'
            assert t.valor == 100.0
            assert t.categoria == 'Hortifruti'
    
    def test_criar_transacao_receita(self, app):
        """Testa criação de transação de receita."""
        with app.app_context():
            t = Transacao(
                tipo='RECEITA',
                valor=5000.0,
                categoria='Vendas',
                data=date(2025, 12, 26)
            )
            db.session.add(t)
            db.session.commit()
            
            assert t.id is not None
            assert t.tipo == 'RECEITA'
            assert t.valor == 5000.0
    
    def test_transacao_to_dict(self, app):
        """Testa conversão de transação para dicionário."""
        with app.app_context():
            t = Transacao(
                tipo='DESPESA',
                valor=250.50,
                categoria='Bebidas',
                descricao='Compra de refrigerantes',
                data=date(2025, 12, 26)
            )
            db.session.add(t)
            db.session.commit()
            
            t_dict = t.to_dict()
            
            assert 'id' in t_dict
            assert t_dict['tipo'] == 'DESPESA'
            assert t_dict['valor'] == 250.50
            assert t_dict['categoria'] == 'Bebidas'
    
    def test_transacao_data_criacao(self, app):
        """Testa que data_criacao é definida automaticamente."""
        with app.app_context():
            t = Transacao(
                tipo='DESPESA',
                valor=50.0,
                categoria='Outros'
            )
            db.session.add(t)
            db.session.commit()
            
            assert t.data_criacao is not None


# =============================================================================
# TESTES: Funções de Consulta
# =============================================================================

class TestConsultas:
    """Testes para funções de consulta de transações."""
    
    def test_get_transacoes_mes_vazio(self, app):
        """Testa consulta em mês sem transações."""
        with app.app_context():
            transacoes = get_transacoes_mes(2025, 1)
            assert transacoes == []
    
    def test_get_transacoes_mes_com_dados(self, app):
        """Testa consulta em mês com transações."""
        with app.app_context():
            # Cria transação
            t = Transacao(
                tipo='DESPESA',
                valor=100.0,
                categoria='Outros',
                data=date(2025, 12, 15)
            )
            db.session.add(t)
            db.session.commit()
            
            transacoes = get_transacoes_mes(2025, 12)
            assert len(transacoes) == 1
            assert transacoes[0].valor == 100.0
    
    def test_get_totais_mes_vazio(self, app):
        """Testa totais em mês sem transações."""
        with app.app_context():
            totais = get_totais_mes(2025, 1)
            
            assert totais['receitas'] == 0
            assert totais['despesas'] == 0
            assert totais['lucro'] == 0
    
    def test_get_totais_mes_com_dados(self, app):
        """Testa totais em mês com transações."""
        with app.app_context():
            # Cria despesa
            t1 = Transacao(
                tipo='DESPESA',
                valor=500.0,
                categoria='Outros',
                data=date(2025, 12, 15)
            )
            # Cria receita
            t2 = Transacao(
                tipo='RECEITA',
                valor=1000.0,
                categoria='Vendas',
                data=date(2025, 12, 15)
            )
            db.session.add_all([t1, t2])
            db.session.commit()
            
            totais = get_totais_mes(2025, 12)
            
            assert totais['despesas'] == 500.0
            assert totais['receitas'] == 1000.0
            assert totais['lucro'] == 500.0
