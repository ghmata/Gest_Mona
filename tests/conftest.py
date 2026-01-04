"""
Configuração do Pytest para o GestorBot.

Este módulo contém fixtures compartilhadas para todos os testes:
- app: Instância Flask configurada para testes
- client: Cliente de teste HTTP
- db_session: Sessão de banco para testes com transação
"""

import pytest
from app import create_app
from models import db as _db


@pytest.fixture(scope='session')
def app():
    """
    Cria instância da aplicação Flask para testes.
    
    Configurações:
    - TESTING: True (modo de teste)
    - DATABASE: SQLite em memória (isolado)
    - WTF_CSRF_ENABLED: False (facilita testes)
    """
    config_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    }
    
    app = create_app(config_override)
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db_session(app):
    """
    Fornece sessão de banco com rollback automático após cada teste.
    
    Garante isolamento entre testes - alterações são revertidas.
    """
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        
        yield _db.session
        
        _db.session.rollback()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='function')
def client(app):
    """
    Cliente de teste para fazer requisições HTTP.
    
    Exemplo de uso:
        def test_home(client):
            response = client.get('/')
            assert response.status_code == 200
    """
    return app.test_client()


@pytest.fixture
def sample_transacao_data():
    """Dados de exemplo para criar uma transação."""
    return {
        'tipo': 'DESPESA',
        'valor': 150.50,
        'data': '2025-12-26',
        'categoria': 'Hortifruti',
        'descricao': 'Compras semanais',
        'estabelecimento': 'CEASA'
    }


@pytest.fixture
def sample_receita_data():
    """Dados de exemplo para criar uma receita."""
    return {
        'tipo': 'RECEITA',
        'valor': 5000.00,
        'data': '2025-12-26',
        'categoria': 'Vendas',
        'descricao': 'Fechamento do dia'
    }
