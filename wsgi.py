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

# Importa a aplicação Flask
from app import app as application


# Inicializa o banco de dados
with application.app_context():
    from models import db
    db.create_all()
