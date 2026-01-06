"""
Blueprint para rotas de autenticação.

Este módulo contém as rotas:
- Login (/login)
- Logout (/logout)
"""

import logging
from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user

from config import Config
from models import db, User

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__)


def get_limiter():
    """Obtém o limiter da aplicação atual."""
    return current_app.limiter


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Exibe formulário de login e processa autenticação."""
    # Aplicar rate limit manualmente (10 tentativas por minuto por IP)
    limiter = get_limiter()
    limiter.limit("10 per minute")(lambda: None)()
    
    # Se já está logado, redireciona para home
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        # Log da tentativa de login
        logger.info(f"Tentativa de login: {email}")
        
        # Busca usuário por email
        user = User.query.filter_by(email=email).first()
        
        if user is None:
            logger.warning(f"Login falhou - usuário não encontrado: {email}")
            flash('Email ou senha inválidos.', 'danger')
            return render_template('login.html')
        
        if not user.ativo:
            logger.warning(f"Login falhou - conta desativada: {email}")
            flash('Sua conta está desativada. Contate o administrador.', 'danger')
            return render_template('login.html')
        
        if not user.check_password(password):
            logger.warning(f"Login falhou - senha incorreta: {email}")
            flash('Email ou senha inválidos.', 'danger')
            return render_template('login.html')
        
        # Login bem-sucedido
        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Login bem-sucedido: {email}")
        flash(f'Bem-vindo, {user.nome}!', 'success')
        
        # Redireciona para a página que o usuário tentava acessar
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.home'))
    
    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    """Encerra sessão do usuário."""
    nome = current_user.nome
    logout_user()
    logger.info(f"Logout realizado: {nome}")
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))
