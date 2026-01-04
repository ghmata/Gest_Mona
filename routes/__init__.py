"""
Pacote de rotas (Blueprints) do GestorBot.

Este pacote contém os blueprints Flask organizados por funcionalidade:
- main: Páginas principais (home, dashboard, receita)
- upload: Endpoints de upload de arquivos
- transacoes: CRUD de transações
- api: Endpoints JSON para dados
"""

from flask import Blueprint

# Imports dos blueprints individuais para facilitar registro
from routes.main import bp as main_bp
from routes.upload import bp as upload_bp
from routes.transacoes import bp as transacoes_bp
from routes.api import bp as api_bp

__all__ = ['main_bp', 'upload_bp', 'transacoes_bp', 'api_bp']
