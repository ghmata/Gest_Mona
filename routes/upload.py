"""
Blueprint para rotas de upload de arquivos do GestorBot.

Este módulo contém as rotas para:
- Upload de nota fiscal única
- Upload de múltiplas notas (em massa)
- Upload de comprovante de receita
"""

import base64
import time
import logging
from datetime import datetime
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app

from config import Config
from services.groq_service import get_groq_service
from utils.file_handler import salvar_arquivo
from utils.pdf_converter import converter_pdf_para_imagem, eh_pdf
from utils.auth_decorators import auth_if_enabled

logger = logging.getLogger(__name__)

bp = Blueprint('upload', __name__)


@bp.route('/upload-nota', methods=['POST'])
@auth_if_enabled
def upload_nota():
    """
    Recebe imagem ou PDF de nota fiscal e processa com IA.
    
    Request JSON:
        {
            "imagem": "data:image/jpeg;base64,...",
            "tipo_arquivo": "imagem" ou "pdf",
            "nome_arquivo": "nota.pdf"
        }
    
    Response JSON:
        {"sucesso": true, "dados": {...}, "comprovante_url": "..."}
    """
    try:
        # Rate limit: 30 uploads por minuto por IP
        limiter = current_app.limiter
        limiter.limit("30 per minute")(lambda: None)()
        
        data = request.get_json()
        if not data:
            return jsonify({
                'sucesso': False,
                'erro': 'Requisição inválida. Envie um JSON com a imagem.'
            }), 400
        
        arquivo_base64 = data.get('imagem')
        if not arquivo_base64:
            return jsonify({
                'sucesso': False,
                'erro': 'Campo "imagem" é obrigatório.'
            }), 400
        
        tipo_arquivo = data.get('tipo_arquivo', 'imagem')
        nome_arquivo_original = data.get('nome_arquivo', '')
        
        # Extrai nome do arquivo para usar como observação
        observacao_arquivo = ''
        if nome_arquivo_original:
            if '.' in nome_arquivo_original:
                observacao_arquivo = nome_arquivo_original.rsplit('.', 1)[0]
            else:
                observacao_arquivo = nome_arquivo_original
            observacao_arquivo = observacao_arquivo.replace('_', ' ').replace('-', ' ')
        
        # Detecta se é PDF
        is_pdf = eh_pdf(arquivo_base64) or tipo_arquivo == 'pdf'
        
        # Se for PDF, converte para imagem antes de processar
        imagem_para_ocr = arquivo_base64
        if is_pdf:
            logger.info("Detectado PDF - convertendo para imagem...")
            imagem_convertida = converter_pdf_para_imagem(arquivo_base64)
            
            if not imagem_convertida:
                return jsonify({
                    'sucesso': False,
                    'erro': 'Não foi possível processar o PDF.'
                }), 400
            
            imagem_para_ocr = imagem_convertida
            logger.info("PDF convertido com sucesso")
        
        # Salva arquivo original no disco
        try:
            comprovante_url = salvar_arquivo(arquivo_base64, tipo_arquivo)
        except ValueError as e:
            return jsonify({
                'sucesso': False,
                'erro': str(e)
            }), 400
        
        # Processa com IA
        service = get_groq_service()
        resultado = service.processar_nota(imagem_para_ocr, nome_arquivo_original)
        
        if not resultado['sucesso']:
            return jsonify({
                'sucesso': False,
                'erro': resultado.get('erro', 'Erro ao processar nota fiscal.')
            }), 400
        
        # Adiciona observação baseada no nome do arquivo
        dados_resposta = resultado['dados']
        if observacao_arquivo:
            dados_resposta['observacao'] = observacao_arquivo
        
        return jsonify({
            'sucesso': True,
            'dados': dados_resposta,
            'comprovante_url': comprovante_url
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no upload de nota: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro interno ao processar a nota.'
        }), 500


@bp.route('/upload-notas-massa', methods=['POST'])
@auth_if_enabled
def upload_notas_massa():
    """
    Processa múltiplos arquivos de notas fiscais (máximo 10).
    
    Request JSON:
        {"arquivos": [{"imagem": "...", "nome_arquivo": "..."}, ...]}
    """
    try:
        # Rate limit: 5 uploads em massa por minuto por IP
        limiter = current_app.limiter
        limiter.limit("5 per minute")(lambda: None)()
        
        data = request.get_json()
        if not data:
            return jsonify({
                'sucesso': False,
                'erro': 'Requisição inválida.'
            }), 400
        
        arquivos = data.get('arquivos', [])
        
        if not arquivos:
            return jsonify({
                'sucesso': False,
                'erro': 'Nenhum arquivo enviado.'
            }), 400
        
        MAX_ARQUIVOS = 10
        if len(arquivos) > MAX_ARQUIVOS:
            return jsonify({
                'sucesso': False,
                'erro': f'Máximo de {MAX_ARQUIVOS} arquivos por vez.'
            }), 400
        
        resultados = []
        total_sucesso = 0
        total_erro = 0
        
        service = get_groq_service()
        
        for i, arquivo in enumerate(arquivos):
            if i > 0:
                time.sleep(2)  # Rate limit
            
            try:
                arquivo_base64 = arquivo.get('imagem', '')
                nome_arquivo = arquivo.get('nome_arquivo', f'arquivo_{i+1}')
                tipo_arquivo = arquivo.get('tipo_arquivo', 'imagem')
                
                if not arquivo_base64:
                    resultados.append({
                        'sucesso': False,
                        'erro': 'Arquivo vazio',
                        'nome_arquivo': nome_arquivo
                    })
                    total_erro += 1
                    continue
                
                is_pdf = eh_pdf(arquivo_base64) or tipo_arquivo == 'pdf'
                
                imagem_para_ocr = arquivo_base64
                if is_pdf:
                    imagem_convertida = converter_pdf_para_imagem(arquivo_base64)
                    if imagem_convertida:
                        imagem_para_ocr = imagem_convertida
                    else:
                        resultados.append({
                            'sucesso': False,
                            'erro': 'Não foi possível processar o PDF',
                            'nome_arquivo': nome_arquivo
                        })
                        total_erro += 1
                        continue
                
                try:
                    comprovante_url = salvar_arquivo(arquivo_base64, tipo_arquivo)
                except ValueError as e:
                    resultados.append({
                        'sucesso': False,
                        'erro': str(e),
                        'nome_arquivo': nome_arquivo
                    })
                    total_erro += 1
                    continue
                
                resultado = service.processar_nota(imagem_para_ocr, nome_arquivo)
                
                if resultado['sucesso']:
                    dados_resposta = resultado['dados']
                    if nome_arquivo:
                        observacao = nome_arquivo.rsplit('.', 1)[0] if '.' in nome_arquivo else nome_arquivo
                        dados_resposta['observacao'] = observacao.replace('_', ' ').replace('-', ' ')
                    
                    resultados.append({
                        'sucesso': True,
                        'dados': dados_resposta,
                        'comprovante_url': comprovante_url,
                        'nome_arquivo': nome_arquivo
                    })
                    total_sucesso += 1
                else:
                    resultados.append({
                        'sucesso': False,
                        'erro': resultado.get('erro', 'Erro ao processar'),
                        'nome_arquivo': nome_arquivo
                    })
                    total_erro += 1
                    
            except Exception as e:
                logger.error(f"Erro ao processar arquivo {i+1}: {e}")
                resultados.append({
                    'sucesso': False,
                    'erro': f'Erro interno: {str(e)[:50]}',
                    'nome_arquivo': arquivo.get('nome_arquivo', f'arquivo_{i+1}')
                })
                total_erro += 1
        
        return jsonify({
            'sucesso': True,
            'total_processados': total_sucesso,
            'total_erros': total_erro,
            'resultados': resultados
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no upload em massa: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro interno ao processar os arquivos.'
        }), 500


@bp.route('/upload-comprovante', methods=['POST'])
@auth_if_enabled
def upload_comprovante():
    """
    Salva um comprovante de receita e processa OCR.
    
    Request JSON:
        {"arquivo": "data:image/jpeg;base64,..."}
    """
    try:
        # Rate limit: 30 uploads por minuto por IP
        limiter = current_app.limiter
        limiter.limit("30 per minute")(lambda: None)()
        
        data = request.get_json()
        if not data or not data.get('arquivo'):
            return jsonify({
                'sucesso': False,
                'erro': 'Arquivo não enviado.'
            }), 400
        
        arquivo_base64_original = data.get('arquivo')
        
        is_pdf = 'application/pdf' in arquivo_base64_original or eh_pdf(arquivo_base64_original)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extensao = 'pdf' if is_pdf else 'jpg'
        filename = f"comprovante_{timestamp}.{extensao}"
        
        arquivo_base64 = arquivo_base64_original
        if 'base64,' in arquivo_base64:
            arquivo_base64 = arquivo_base64.split('base64,')[1]
        
        arquivo_bytes = base64.b64decode(arquivo_base64.strip())
        
        upload_folder = Path(Config.UPLOAD_FOLDER)
        upload_folder.mkdir(parents=True, exist_ok=True)
        
        filepath = upload_folder / filename
        with open(filepath, 'wb') as f:
            f.write(arquivo_bytes)
        
        logger.info(f"Comprovante salvo: {filepath}")
        
        comprovante_url = f"/static/uploads/{filename}"
        
        imagem_para_ocr = arquivo_base64_original
        if is_pdf:
            imagem_convertida = converter_pdf_para_imagem(arquivo_base64_original)
            if imagem_convertida:
                imagem_para_ocr = imagem_convertida
        
        service = get_groq_service()
        resultado = service.processar_receita(imagem_para_ocr)
        
        if resultado['sucesso']:
            return jsonify({
                'sucesso': True,
                'url': comprovante_url,
                'dados': resultado['dados']
            }), 200
        else:
            return jsonify({
                'sucesso': True,
                'url': comprovante_url,
                'dados': None,
                'aviso': resultado.get('erro', 'Não foi possível extrair dados.')
            }), 200
        
    except Exception as e:
        logger.error(f"Erro ao salvar comprovante: {e}")
        return jsonify({
            'sucesso': False,
            'erro': 'Erro ao salvar comprovante.'
        }), 500
