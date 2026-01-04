"""
Módulo de funções auxiliares do GestorBot.

Este módulo contém funções utilitárias para validação de dados,
formatação de valores e extração de informações estruturadas.
"""

# 1. Bibliotecas padrão
import json
import re
import logging
from datetime import datetime
from typing import Optional, Union

# Configuração de logging
logger = logging.getLogger(__name__)


def extrair_json_de_texto(texto: str) -> Optional[dict]:
    """
    Extrai JSON de texto que pode conter markdown ou texto adicional.
    
    Procura por padrões JSON válidos no texto e tenta parseá-los.
    Útil para extrair dados estruturados de respostas de LLMs que
    podem incluir explicações ou formatação markdown.
    
    Args:
        texto: Texto que pode conter JSON em algum lugar
    
    Returns:
        dict: Dicionário parseado do JSON encontrado, ou None se não encontrar
    
    Example:
        >>> texto = "Aqui está o resultado: {\"valor\": 100}"
        >>> extrair_json_de_texto(texto)
        {'valor': 100}
    """
    if not texto:
        logger.warning("Texto vazio recebido para extração de JSON")
        return None
    
    try:
        # Primeiro, tenta parsear o texto inteiro como JSON
        return json.loads(texto.strip())
    except json.JSONDecodeError:
        pass
    
    try:
        # Tenta encontrar JSON dentro de blocos de código markdown
        # Padrão: ```json ... ``` ou ``` ... ```
        padrao_markdown = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
        match = re.search(padrao_markdown, texto)
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
    except json.JSONDecodeError:
        logger.debug("Falha ao parsear JSON de bloco markdown")
    
    try:
        # Procura por { ... } no texto
        inicio = texto.find('{')
        fim = texto.rfind('}')
        
        if inicio != -1 and fim != -1 and fim > inicio:
            json_str = texto[inicio:fim + 1]
            return json.loads(json_str)
    except json.JSONDecodeError:
        logger.debug("Falha ao parsear JSON extraído do texto")
    
    logger.warning(f"Não foi possível extrair JSON do texto: {texto[:100]}...")
    return None


def validar_data(data_str: str) -> bool:
    """
    Valida se string está no formato YYYY-MM-DD válido.
    
    Args:
        data_str: String de data a ser validada
    
    Returns:
        bool: True se a data é válida, False caso contrário
    
    Example:
        >>> validar_data("2025-12-26")
        True
        >>> validar_data("26/12/2025")
        False
        >>> validar_data("2025-13-01")
        False
    """
    if not data_str or not isinstance(data_str, str):
        return False
    
    # Verifica formato básico com regex
    padrao = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(padrao, data_str):
        return False
    
    try:
        # Valida se é uma data real (não aceita 2025-02-30, por exemplo)
        datetime.strptime(data_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def formatar_valor(valor: Union[str, int, float, None]) -> float:
    """
    Converte valor para float, tratando strings com vírgula, R$ e espaços.
    
    Args:
        valor: Valor a ser convertido (pode ser string, int ou float)
    
    Returns:
        float: Valor numérico formatado, ou 0.0 se não for possível converter
    
    Example:
        >>> formatar_valor("R$ 1.234,56")
        1234.56
        >>> formatar_valor("150,50")
        150.5
        >>> formatar_valor(100)
        100.0
    """
    if valor is None:
        return 0.0
    
    # Se já é número, apenas converte para float
    if isinstance(valor, (int, float)):
        return float(valor)
    
    if not isinstance(valor, str):
        logger.warning(f"Tipo inesperado para formatar_valor: {type(valor)}")
        return 0.0
    
    try:
        # Remove espaços e símbolos de moeda
        valor_limpo = valor.strip()
        valor_limpo = valor_limpo.replace('R$', '').strip()
        valor_limpo = valor_limpo.replace(' ', '')
        
        # Detecta formato brasileiro (1.234,56) vs americano (1,234.56)
        # Se tem ponto E vírgula, provavelmente é formato brasileiro
        if '.' in valor_limpo and ',' in valor_limpo:
            # Formato brasileiro: remove pontos de milhar, troca vírgula por ponto
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
        elif ',' in valor_limpo:
            # Apenas vírgula: provavelmente vírgula decimal
            valor_limpo = valor_limpo.replace(',', '.')
        
        resultado = float(valor_limpo)
        
        if resultado < 0:
            logger.warning(f"Valor negativo detectado: {resultado}")
        
        return resultado
    
    except (ValueError, TypeError) as e:
        logger.warning(f"Erro ao formatar valor '{valor}': {e}")
        return 0.0


def converter_data_para_formato_padrao(data_str: str) -> Optional[str]:
    """
    Converte diferentes formatos de data para o formato padrão YYYY-MM-DD.
    
    Args:
        data_str: String de data em diversos formatos possíveis
    
    Returns:
        str: Data no formato YYYY-MM-DD, ou None se não for possível converter
    
    Example:
        >>> converter_data_para_formato_padrao("26/12/2025")
        "2025-12-26"
        >>> converter_data_para_formato_padrao("2025-12-26")
        "2025-12-26"
    """
    if not data_str or not isinstance(data_str, str):
        return None
    
    data_str = data_str.strip()
    
    # Lista de formatos comuns a tentar
    formatos = [
        '%Y-%m-%d',    # 2025-12-26
        '%d/%m/%Y',    # 26/12/2025
        '%d-%m-%Y',    # 26-12-2025
        '%d.%m.%Y',    # 26.12.2025
        '%Y/%m/%d',    # 2025/12/26
    ]
    
    for formato in formatos:
        try:
            data = datetime.strptime(data_str, formato)
            return data.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    logger.warning(f"Não foi possível converter a data: {data_str}")
    return None
