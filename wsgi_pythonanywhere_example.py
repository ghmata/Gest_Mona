
# +++++++++++ FLASK +++++++++++
# Flask works like any other WSGI-compatible framework, we just need
# to import the application.  Often Flask apps are called "app" so we
# may need to import it somewhat differently:

# import sys
#
# The project folder must be in sys.path
# project_home = '/home/Hip00/MONA_Controle_financeiro'
# if project_home not in sys.path:
#     sys.path = [project_home] + sys.path

# Load .env file explicitly
# from dotenv import load_dotenv
# import os
# project_folder = os.path.expanduser('~/MONA_Controle_financeiro')  # adjust as appropriate
# load_dotenv(os.path.join(project_folder, '.env'))

# import flask app but need to call it "application" for WSGI to work
# from app import app as application  # noqa
