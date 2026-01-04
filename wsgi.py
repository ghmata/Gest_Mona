"""
Arquivo WSGI para PythonAnywhere.

Este arquivo é o ponto de entrada para o servidor WSGI do PythonAnywhere.
Configure no PythonAnywhere:
  Source code: /home/SEU_USUARIO/MONA_v1
  Working directory: /home/SEU_USUARIO/MONA_v1
  WSGI configuration file: /var/www/SEU_USUARIO_pythonanywhere_com_wsgi.py

No arquivo WSGI do PythonAnywhere, adicione:
  import sys
  sys.path.insert(0, '/home/SEU_USUARIO/MONA_v1')
  from wsgi import application
"""

import sys
import os

# Adiciona o diretório do projeto ao path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Importa a aplicação Flask
from app import app as application

# Inicializa o banco de dados
with application.app_context():
    from models import db
    db.create_all()
