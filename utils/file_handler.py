"""
Módulo para manipulação de arquivos do GestorBot.

Este módulo contém funções para salvar arquivos base64 (imagens e PDFs)
no sistema de arquivos.
"""

import base64
import logging
from datetime import datetime
from pathlib import Path

from config import Config

logger = logging.getLogger(__name__)


def salvar_arquivo(arquivo_base64: str, tipo_arquivo: str = 'imagem') -> str:
    """
    Salva arquivo base64 (imagem ou PDF) no disco.
    
    Args:
        arquivo_base64: String base64 (com ou sem prefixo data:)
        tipo_arquivo: 'imagem' ou 'pdf'
    
    Returns:
        str: URL relativa do arquivo salvo (ex: /static/uploads/nota_xxx.jpg)
    
    Raises:
        ValueError: Se o arquivo for inválido ou não puder ser salvo
    """
    try:
        # Detecta o tipo pelo prefixo base64
        is_pdf = 'application/pdf' in arquivo_base64 or tipo_arquivo == 'pdf'
        
        # Remove prefixo data:xxx;base64, se existir
        if 'base64,' in arquivo_base64:
            arquivo_base64 = arquivo_base64.split('base64,')[1]
        
        # Remove espaços e quebras de linha
        arquivo_base64 = arquivo_base64.strip().replace('\n', '').replace('\r', '')
        
        # Decodifica base64
        arquivo_bytes = base64.b64decode(arquivo_base64)
        
        # Gera nome único com timestamp e extensão apropriada
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extensao = 'pdf' if is_pdf else 'jpg'
        filename = f"nota_{timestamp}.{extensao}"
        
        # Garante que a pasta existe
        upload_folder = Path(Config.UPLOAD_FOLDER)
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        # Salva o arquivo
        filepath = upload_folder / filename
        with open(filepath, 'wb') as f:
            f.write(arquivo_bytes)
        
        logger.info(f"Arquivo salvo: {filepath} (tipo: {tipo_arquivo})")
        
        # Retorna URL relativa
        return f"/static/uploads/{filename}"
        
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo: {e}")
        raise ValueError(f"Não foi possível salvar o arquivo: {e}")


def salvar_imagem(imagem_base64: str) -> str:
    """Alias para salvar_arquivo (compatibilidade)."""
    return salvar_arquivo(imagem_base64, 'imagem')
