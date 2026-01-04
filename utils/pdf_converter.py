"""
Módulo de conversão de PDF para imagem.

Utiliza PyMuPDF (fitz) para converter a primeira página de um PDF
em uma imagem JPEG para processamento pelo OCR.
"""

# 1. Bibliotecas padrão
import base64
import io
import logging
from typing import Optional, Tuple

# Configuração de logging
logger = logging.getLogger(__name__)

# Tentar importar PyMuPDF
try:
    import fitz  # PyMuPDF
    PYMUPDF_DISPONIVEL = True
except ImportError:
    PYMUPDF_DISPONIVEL = False
    logger.warning(
        "PyMuPDF não instalado. Conversão de PDF para imagem não disponível. "
        "Instale com: pip install pymupdf"
    )


def converter_pdf_para_imagem(pdf_base64: str, dpi: int = 150) -> Optional[str]:
    """
    Converte a primeira página de um PDF para imagem JPEG em base64.
    
    Args:
        pdf_base64: String base64 do PDF (com ou sem prefixo data:)
        dpi: Resolução da imagem gerada (default: 150)
    
    Returns:
        str: String base64 da imagem JPEG, ou None se falhar
    
    Example:
        >>> with open("nota.pdf", "rb") as f:
        ...     pdf_b64 = base64.b64encode(f.read()).decode()
        >>> img_b64 = converter_pdf_para_imagem(pdf_b64)
    """
    if not PYMUPDF_DISPONIVEL:
        logger.error("PyMuPDF não está disponível para conversão de PDF")
        return None
    
    try:
        # Remove prefixo data:xxx;base64, se existir
        if 'base64,' in pdf_base64:
            pdf_base64 = pdf_base64.split('base64,')[1]
        
        # Remove espaços e quebras de linha
        pdf_base64 = pdf_base64.strip().replace('\n', '').replace('\r', '')
        
        # Decodifica base64
        pdf_bytes = base64.b64decode(pdf_base64)
        
        # Abre o PDF com PyMuPDF
        documento = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if documento.page_count == 0:
            logger.warning("PDF não contém páginas")
            documento.close()
            return None
        
        # Pega a primeira página
        pagina = documento[0]
        
        # Renderiza como imagem (matriz de zoom baseada no DPI)
        zoom = dpi / 72  # 72 é o DPI padrão do PDF
        matriz = fitz.Matrix(zoom, zoom)
        
        # Gera o pixmap (imagem)
        pixmap = pagina.get_pixmap(matrix=matriz)
        
        # Converte para bytes JPEG
        img_bytes = pixmap.tobytes("jpeg")
        
        # Fecha o documento
        documento.close()
        
        # Converte para base64
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        logger.info(f"PDF convertido para imagem: {len(img_bytes)} bytes")
        
        # Retorna com prefixo data:image
        return f"data:image/jpeg;base64,{img_base64}"
        
    except Exception as e:
        logger.error(f"Erro ao converter PDF para imagem: {e}")
        return None


def eh_pdf(arquivo_base64: str) -> bool:
    """
    Verifica se o arquivo base64 é um PDF.
    
    Args:
        arquivo_base64: String base64 do arquivo
    
    Returns:
        bool: True se for PDF, False caso contrário
    """
    # Verifica pelo prefixo data:
    if 'application/pdf' in arquivo_base64:
        return True
    
    # Verifica pelos magic bytes do PDF (%PDF-)
    try:
        if 'base64,' in arquivo_base64:
            dados = arquivo_base64.split('base64,')[1]
        else:
            dados = arquivo_base64
        
        # Decodifica os primeiros bytes
        dados_limpos = dados.strip().replace('\n', '').replace('\r', '')
        primeiros_bytes = base64.b64decode(dados_limpos[:20])
        
        # PDF começa com %PDF-
        return primeiros_bytes.startswith(b'%PDF-')
        
    except Exception:
        return False


def obter_info_pdf(pdf_base64: str) -> Optional[dict]:
    """
    Obtém informações básicas sobre um PDF.
    
    Args:
        pdf_base64: String base64 do PDF
    
    Returns:
        dict: {num_paginas: int, tamanho_kb: float} ou None se falhar
    """
    if not PYMUPDF_DISPONIVEL:
        return None
    
    try:
        if 'base64,' in pdf_base64:
            pdf_base64 = pdf_base64.split('base64,')[1]
        
        pdf_bytes = base64.b64decode(pdf_base64.strip())
        documento = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        info = {
            'num_paginas': documento.page_count,
            'tamanho_kb': len(pdf_bytes) / 1024
        }
        
        documento.close()
        return info
        
    except Exception as e:
        logger.error(f"Erro ao obter info do PDF: {e}")
        return None
