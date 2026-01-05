"""
Decorators auxiliares para autenticação e controle de acesso.
"""

from functools import wraps

from flask import abort, redirect, url_for
from flask_login import current_user, login_required

from config import Config


def admin_required(f):
    """
    Decorator que requer que o usuário seja administrador.
    
    Uso:
        @bp.route('/admin/rota')
        @admin_required
        def rota_admin():
            ...
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def auth_if_enabled(f):
    """
    Decorator condicional de autenticação.
    
    Se AUTH_ENABLED=True, requer login.
    Se AUTH_ENABLED=False, permite acesso livre.
    
    Uso:
        @bp.route('/dashboard')
        @auth_if_enabled
        def dashboard():
            ...
    """
    if Config.AUTH_ENABLED:
        return login_required(f)
    return f
