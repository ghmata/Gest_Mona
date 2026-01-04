"""
Testes para rotas HTTP (endpoints).

Testa:
- Rotas principais: home, dashboard
- Rotas de API: transações, totais
"""

import pytest
import json


# =============================================================================
# TESTES: Rotas Principais
# =============================================================================

class TestRotasPrincipais:
    """Testes para rotas de páginas."""
    
    def test_home_status_ok(self, client):
        """Testa que home retorna status 200."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_home_contem_html(self, client):
        """Testa que home retorna HTML."""
        response = client.get('/')
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
    
    def test_dashboard_status_ok(self, client):
        """Testa que dashboard retorna status 200."""
        response = client.get('/dashboard')
        assert response.status_code == 200
    
    def test_dashboard_com_parametros(self, client):
        """Testa dashboard com parâmetros de mês/ano."""
        response = client.get('/dashboard?mes=12&ano=2025')
        assert response.status_code == 200
    
    def test_receita_status_ok(self, client):
        """Testa que formulário de receita retorna status 200."""
        response = client.get('/receita')
        assert response.status_code == 200


# =============================================================================
# TESTES: API de Transações
# =============================================================================

class TestApiTransacoes:
    """Testes para endpoints de transações."""
    
    def test_listar_transacoes_vazio(self, client):
        """Testa listagem de transações quando vazio."""
        response = client.get('/transacoes')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'transacoes' in data
        assert 'total' in data
    
    def test_criar_transacao_valida(self, client, sample_transacao_data):
        """Testa criação de transação válida."""
        response = client.post(
            '/transacao',
            data=json.dumps(sample_transacao_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['sucesso'] is True
        assert 'id' in data
    
    def test_criar_transacao_sem_tipo(self, client):
        """Testa criação de transação sem tipo (erro)."""
        response = client.post(
            '/transacao',
            data=json.dumps({'valor': 100}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['sucesso'] is False
    
    def test_criar_transacao_sem_valor(self, client):
        """Testa criação de transação sem valor (erro)."""
        response = client.post(
            '/transacao',
            data=json.dumps({'tipo': 'DESPESA', 'data': '2025-12-26', 'categoria': 'Outros'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['sucesso'] is False
    
    def test_criar_transacao_data_invalida(self, client):
        """Testa criação de transação com data inválida."""
        response = client.post(
            '/transacao',
            data=json.dumps({
                'tipo': 'DESPESA',
                'valor': 100,
                'data': '26/12/2025',  # Formato errado
                'categoria': 'Outros'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400


# =============================================================================
# TESTES: API de Totais
# =============================================================================

class TestApiTotais:
    """Testes para endpoint de totais."""
    
    def test_api_totais_status_ok(self, client):
        """Testa que API de totais retorna status 200."""
        response = client.get('/api/totais')
        assert response.status_code == 200
    
    def test_api_totais_estrutura(self, client):
        """Testa estrutura de resposta da API de totais."""
        response = client.get('/api/totais')
        data = json.loads(response.data)
        
        assert 'sucesso' in data
        assert data['sucesso'] is True
        assert 'faturamento' in data
        assert 'gastos' in data
        assert 'lucro' in data
    
    def test_api_totais_com_parametros(self, client):
        """Testa API de totais com parâmetros."""
        response = client.get('/api/totais?mes=12&ano=2025')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['mes'] == 12
        assert data['ano'] == 2025
