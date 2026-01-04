"""
Script para limpar o banco de dados do GestorBot.
Deleta todas as transações mantendo a estrutura das tabelas.

Uso: python limpar_banco.py
"""

from app import app, db
from models import Transacao

def limpar_banco():
    """Remove todas as transações do banco de dados."""
    with app.app_context():
        # Conta transações antes de deletar
        total = Transacao.query.count()
        
        if total == 0:
            print("✅ O banco de dados já está vazio!")
            return
        
        # Deleta todas as transações
        Transacao.query.delete()
        db.session.commit()
        
        print(f"✅ Banco de dados limpo com sucesso!")
        print(f"   {total} transação(ões) removida(s).")

if __name__ == '__main__':
    confirmacao = input("⚠️  Tem certeza que deseja apagar TODOS os dados? (s/n): ")
    
    if confirmacao.lower() in ['s', 'sim', 'y', 'yes']:
        limpar_banco()
    else:
        print("❌ Operação cancelada.")
