"""
Blueprint para rotas de administração.

Este módulo contém as rotas:
- Lista de usuários (/admin/usuarios)
- Criar usuário (/admin/usuarios/novo)
- Editar usuário (/admin/usuarios/<id>/editar)
- Toggle ativo/inativo (/admin/usuarios/<id>/toggle)
- Reset de senha (/admin/usuarios/<id>/reset-senha)
"""

import logging
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from config import Config
from models import db, User
from utils.auth_decorators import admin_required

logger = logging.getLogger(__name__)

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/usuarios')
@admin_required
def usuarios():
    """Lista todos os usuários do sistema."""
    users = User.query.order_by(User.nome).all()
    return render_template('admin/usuarios.html', usuarios=users)


@bp.route('/usuarios/novo', methods=['GET', 'POST'])
@admin_required
def usuario_novo():
    """Formulário para criar novo usuário."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        nome = request.form.get('nome', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'user')
        
        # Validações
        if not email or not nome or not password:
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('admin/usuario_form.html', usuario=None, modo='novo')
        
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'danger')
            return render_template('admin/usuario_form.html', usuario=None, modo='novo')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('admin/usuario_form.html', usuario=None, modo='novo')
        
        # Cria usuário
        user = User(email=email, nome=nome, role=role, ativo=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Usuário criado: {email} por {request.remote_addr}")
        flash(f'Usuário {nome} criado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', usuario=None, modo='novo')


@bp.route('/usuarios/<int:user_id>/editar', methods=['GET', 'POST'])
@admin_required
def usuario_editar(user_id):
    """Formulário para editar usuário existente."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        nome = request.form.get('nome', '').strip()
        role = request.form.get('role', 'user')
        
        # Validações
        if not email or not nome:
            flash('Email e nome são obrigatórios.', 'danger')
            return render_template('admin/usuario_form.html', usuario=user, modo='editar')
        
        # Verifica se email já existe (outro usuário)
        existing = User.query.filter_by(email=email).first()
        if existing and existing.id != user_id:
            flash('Este email já está cadastrado.', 'danger')
            return render_template('admin/usuario_form.html', usuario=user, modo='editar')
        
        # Atualiza dados
        user.email = email
        user.nome = nome
        user.role = role
        db.session.commit()
        
        logger.info(f"Usuário editado: {email}")
        flash(f'Usuário {nome} atualizado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', usuario=user, modo='editar')


@bp.route('/usuarios/<int:user_id>/toggle', methods=['POST'])
@admin_required
def usuario_toggle(user_id):
    """Ativa ou desativa um usuário."""
    user = User.query.get_or_404(user_id)
    
    # Não permite desativar a si mesmo
    from flask_login import current_user
    if user.id == current_user.id:
        flash('Você não pode desativar sua própria conta.', 'danger')
        return redirect(url_for('admin.usuarios'))
    
    user.ativo = not user.ativo
    db.session.commit()
    
    status = "ativado" if user.ativo else "desativado"
    logger.info(f"Usuário {user.email} {status}")
    flash(f'Usuário {user.nome} {status}.', 'success')
    return redirect(url_for('admin.usuarios'))


@bp.route('/usuarios/<int:user_id>/reset-senha', methods=['POST'])
@admin_required
def usuario_reset_senha(user_id):
    """Reseta a senha de um usuário."""
    user = User.query.get_or_404(user_id)
    nova_senha = request.form.get('nova_senha', '')
    
    if len(nova_senha) < 6:
        flash('A nova senha deve ter pelo menos 6 caracteres.', 'danger')
        return redirect(url_for('admin.usuarios'))
    
    user.set_password(nova_senha)
    db.session.commit()
    
    logger.info(f"Senha resetada para: {user.email}")
    flash(f'Senha de {user.nome} resetada com sucesso!', 'success')
    return redirect(url_for('admin.usuarios'))
