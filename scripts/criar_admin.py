#!/usr/bin/env python
"""
Script para criar usuários administradores iniciais.

Uso:
    python criar_admin.py

Este script cria os usuários admin definidos se não existirem.
Seguro para executar múltiplas vezes (não duplica usuários).
"""

import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User


# Usuários admin iniciais
ADMINS = [
    {
        'email': 'adm',
        'nome': 'Administrador',
        'password': 'IBMG373@',
        'role': 'admin'
    },
    {
        'email': 'mona',
        'nome': 'Mona Admin',
        'password': 'mona2026@',
        'role': 'admin'
    }
]


def criar_admins():
    """Cria usuários admin se não existirem."""
    with app.app_context():
        # Garante que a tabela existe
        db.create_all()
        
        for admin_data in ADMINS:
            # Verifica se já existe
            existing = User.query.filter_by(email=admin_data['email']).first()
            
            if existing:
                print(f"⚠️  Usuário '{admin_data['email']}' já existe. Pulando...")
                continue
            
            # Cria novo usuário
            user = User(
                email=admin_data['email'],
                nome=admin_data['nome'],
                role=admin_data['role'],
                ativo=True
            )
            user.set_password(admin_data['password'])
            db.session.add(user)
            
            print(f"✅ Usuário '{admin_data['email']}' criado com sucesso!")
        
        db.session.commit()
        print("\n🎉 Processo concluído!")
        
        # Lista todos os usuários
        print("\n📋 Usuários cadastrados:")
        for user in User.query.all():
            status = "✓" if user.ativo else "✗"
            print(f"   {status} {user.email} ({user.role})")


if __name__ == '__main__':
    print("=" * 50)
    print("🔐 Criação de Usuários Administradores")
    print("=" * 50)
    print()
    
    criar_admins()
