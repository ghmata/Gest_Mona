"""
Arquivo WSGI para PythonAnywhere.

Este arquivo é o ponto de entrada para o servidor WSGI do PythonAnywhere.
Configure no PythonAnywhere:
  Source code: /home/Hip00/MONA_Controle_financeiro
  Working directory: /home/Hip00/MONA_Controle_financeiro
  WSGI configuration file: /var/www/Hip00_pythonanywhere_com_wsgi.py

No arquivo WSGI do PythonAnywhere, adicione:
  import sys
  sys.path.insert(0, '/home/Hip00/MONA_Controle_financeiro')
  from wsgi import application
"""

import sys
import os

# Adiciona o diretório do projeto ao path
project_home = '/home/Hip00/MONA_Controle_financeiro'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Define o diretório atual para garantir imports relativos
if os.path.isdir(project_home):
    os.chdir(project_home)

# ============================================
# IMPORTANTE: Carregar .env ANTES de importar app
# Isso garante que GROQ_API_KEY esteja disponível
# quando config.py e groq_service.py forem carregados
# ============================================

# Define API Key diretamente (fallback caso .env não funcione)
os.environ.setdefault('GROQ_API_KEY', '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')
os.environ.setdefault('SECRET_KEY', 'ILSHCFSDCSMNT310820010103201928062025')

from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[WSGI] .env carregado de: {env_path}")
else:
    print(f"[WSGI] AVISO: .env não encontrado - usando valores padrao")

# Debug: verifica se GROQ_API_KEY foi carregada
groq_key = os.environ.get('GROQ_API_KEY', '')
if groq_key:
    masked = f"{groq_key[:4]}...{groq_key[-4:]}" if len(groq_key) > 8 else "***"
    print(f"[WSGI] GROQ_API_KEY detectada: {masked}")
else:
    print("[WSGI] AVISO: GROQ_API_KEY não encontrada no ambiente!")

# Importa a aplicação Flask (DEPOIS de carregar o .env)
from app import app as application


# Inicializa o banco de dados
with application.app_context():
    from models import db
    db.create_all()
