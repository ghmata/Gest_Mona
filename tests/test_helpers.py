"""
Testes para funções auxiliares do utils/helpers.py.

Testa:
- formatar_valor: Conversão de strings monetárias para float
- validar_data: Validação de formato de data YYYY-MM-DD
- extrair_json_de_texto: Extração de JSON de texto
- converter_data_para_formato_padrao: Conversão de datas
"""

import pytest
from utils.helpers import (
    formatar_valor,
    validar_data,
    extrair_json_de_texto,
    converter_data_para_formato_padrao
)


# =============================================================================
# TESTES: formatar_valor
# =============================================================================

class TestFormatarValor:
    """Testes para a função formatar_valor."""
    
    def test_formatar_valor_brasileiro(self):
        """Testa formato brasileiro com ponto de milhar e vírgula decimal."""
        assert formatar_valor("R$ 1.234,56") == 1234.56
    
    def test_formatar_valor_brasileiro_simples(self):
        """Testa formato brasileiro sem milhar."""
        assert formatar_valor("150,50") == 150.50
    
    def test_formatar_valor_inteiro(self):
        """Testa valor inteiro."""
        assert formatar_valor(100) == 100.0
    
    def test_formatar_valor_float(self):
        """Testa valor já em float."""
        assert formatar_valor(99.99) == 99.99
    
    def test_formatar_valor_none(self):
        """Testa valor None retorna 0.0."""
        assert formatar_valor(None) == 0.0
    
    def test_formatar_valor_string_simples(self):
        """Testa string numérica simples."""
        assert formatar_valor("250") == 250.0
    
    def test_formatar_valor_com_espaco(self):
        """Testa valor com espaços."""
        assert formatar_valor("  R$ 500,00  ") == 500.0
    
    def test_formatar_valor_americano(self):
        """Testa formato americano com ponto decimal."""
        assert formatar_valor("1234.56") == 1234.56
    
    def test_formatar_valor_invalido(self):
        """Testa valor inválido retorna 0.0."""
        assert formatar_valor("texto inválido") == 0.0


# =============================================================================
# TESTES: validar_data
# =============================================================================

class TestValidarData:
    """Testes para a função validar_data."""
    
    def test_validar_data_valida(self):
        """Testa data válida no formato correto."""
        assert validar_data("2025-12-26") is True
    
    def test_validar_data_primeiro_dia(self):
        """Testa primeiro dia do ano."""
        assert validar_data("2025-01-01") is True
    
    def test_validar_data_ultimo_dia(self):
        """Testa último dia do ano."""
        assert validar_data("2025-12-31") is True
    
    def test_validar_data_formato_brasileiro(self):
        """Testa formato brasileiro (inválido para esta função)."""
        assert validar_data("26/12/2025") is False
    
    def test_validar_data_mes_invalido(self):
        """Testa mês inválido."""
        assert validar_data("2025-13-01") is False
    
    def test_validar_data_dia_invalido(self):
        """Testa dia inválido para o mês."""
        assert validar_data("2025-02-30") is False
    
    def test_validar_data_none(self):
        """Testa None."""
        assert validar_data(None) is False
    
    def test_validar_data_vazia(self):
        """Testa string vazia."""
        assert validar_data("") is False
    
    def test_validar_data_tipo_errado(self):
        """Testa tipo incorreto."""
        assert validar_data(20251226) is False


# =============================================================================
# TESTES: extrair_json_de_texto
# =============================================================================

class TestExtrairJsonDeTexto:
    """Testes para a função extrair_json_de_texto."""
    
    def test_extrair_json_puro(self):
        """Testa extração de JSON puro."""
        texto = '{"valor": 100, "categoria": "Outros"}'
        resultado = extrair_json_de_texto(texto)
        assert resultado == {"valor": 100, "categoria": "Outros"}
    
    def test_extrair_json_com_texto(self):
        """Testa extração de JSON com texto ao redor."""
        texto = 'Aqui está o resultado: {"sucesso": true}'
        resultado = extrair_json_de_texto(texto)
        assert resultado == {"sucesso": True}
    
    def test_extrair_json_markdown(self):
        """Testa extração de JSON de bloco markdown."""
        texto = '```json\n{"data": "2025-12-26"}\n```'
        resultado = extrair_json_de_texto(texto)
        assert resultado == {"data": "2025-12-26"}
    
    def test_extrair_json_vazio(self):
        """Testa texto vazio."""
        assert extrair_json_de_texto("") is None
    
    def test_extrair_json_none(self):
        """Testa None."""
        assert extrair_json_de_texto(None) is None
    
    def test_extrair_json_invalido(self):
        """Testa JSON inválido."""
        assert extrair_json_de_texto("texto sem json") is None


# =============================================================================
# TESTES: converter_data_para_formato_padrao
# =============================================================================

class TestConverterDataParaFormatoPadrao:
    """Testes para a função converter_data_para_formato_padrao."""
    
    def test_converter_formato_brasileiro(self):
        """Testa conversão de formato brasileiro."""
        assert converter_data_para_formato_padrao("26/12/2025") == "2025-12-26"
    
    def test_converter_formato_iso(self):
        """Testa formato ISO já correto."""
        assert converter_data_para_formato_padrao("2025-12-26") == "2025-12-26"
    
    def test_converter_formato_hifen(self):
        """Testa formato com hífen dd-mm-yyyy."""
        assert converter_data_para_formato_padrao("26-12-2025") == "2025-12-26"
    
    def test_converter_formato_ponto(self):
        """Testa formato com ponto dd.mm.yyyy."""
        assert converter_data_para_formato_padrao("26.12.2025") == "2025-12-26"
    
    def test_converter_none(self):
        """Testa None."""
        assert converter_data_para_formato_padrao(None) is None
    
    def test_converter_formato_invalido(self):
        """Testa formato não reconhecido."""
        assert converter_data_para_formato_padrao("December 26, 2025") is None
