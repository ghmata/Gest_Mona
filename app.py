"""
Aplicação Flask para o GestorBot - Gestão Financeira para Restaurantes.

Este módulo contém a aplicação Flask principal (ponto de entrada).
As rotas estão organizadas em blueprints no pacote 'routes'.
"""

# 1. Bibliotecas padrão
import os
import logging

# 2. Bibliotecas externas
from datetime import timedelta
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# 3. Imports locais
from config import Config
from models import db, User

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CRIAÇÃO DA APLICAÇÃO
# =============================================================================

def create_app(config_override: dict = None) -> Flask:
    """
    Factory function para criar a aplicação Flask.
    
    Args:
        config_override: Dicionário com configurações para sobrescrever (útil para testes)
    
    Returns:
        Flask: Instância configurada da aplicação
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configurações adicionais
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Override de configurações (para testes)
    if config_override:
        app.config.update(config_override)
    
    # Inicializar banco de dados
    db.init_app(app)
    
    # Inicializar proteção CSRF
    csrf = CSRFProtect(app)
    
    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = Config.LOGIN_MESSAGE
    login_manager.login_message_category = 'warning'
    
    # Configurar duração do cookie "Lembrar-me"
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=Config.REMEMBER_COOKIE_DURATION)
    
    @login_manager.user_loader
    def load_user(user_id):
        """Callback para carregar usuário da sessão."""
        return User.query.get(int(user_id))
    
    # Inicializar CORS
    # Origins configuráveis via Config.CORS_ORIGINS (env var CORS_ORIGINS)
    cors_origins = Config.CORS_ORIGINS
    CORS(app, resources={
        r"/api/*": {"origins": cors_origins},
        r"/upload-*": {"origins": cors_origins},
        r"/transacao*": {"origins": cors_origins}
    })
    
    # Headers de segurança
    @app.after_request
    def add_security_headers(response):
        """Adiciona headers de segurança em todas as respostas."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    # Registrar blueprints
    from routes.main import bp as main_bp
    from routes.upload import bp as upload_bp
    from routes.transacoes import bp as transacoes_bp
    from routes.api import bp as api_bp
    from routes.auth import bp as auth_bp
    from routes.admin import bp as admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(transacoes_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # Tratamento de erros
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Tratamento para arquivos muito grandes."""
        return jsonify({
            'sucesso': False,
            'erro': f'Arquivo muito grande. Máximo: {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB'
        }), 413

    @app.errorhandler(404)
    def not_found(error):
        """Tratamento para página não encontrada."""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'sucesso': False, 'erro': 'Recurso não encontrado.'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        """Tratamento para acesso negado."""
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'sucesso': False, 'erro': 'Acesso negado.'}), 403
        return render_template('403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        """Tratamento para erro interno."""
        db.session.rollback()
        logger.error(f"Erro interno: {error}")
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({'sucesso': False, 'erro': 'Erro interno do servidor.'}), 500
        return render_template('500.html'), 500
    
    return app


# Criação da instância para compatibilidade com imports existentes
app = create_app()


# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

def init_db():
    """Cria as tabelas do banco de dados se não existirem."""
    with app.app_context():
        db.create_all()
        logger.info("✅ Banco de dados inicializado")


if __name__ == '__main__':
    # Criar pasta de uploads se não existir
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Verificar configurações
    Config.verificar_configuracoes()
    
    # Inicializar banco
    init_db()
    
    # Configurações do servidor
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    logger.info(f"🚀 GestorBot iniciando em http://{host}:{port}")
    app.run(debug=debug_mode, host=host, port=port)
