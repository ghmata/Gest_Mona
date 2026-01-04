"""
Script de migração para adicionar coluna subcategoria à tabela transacoes (MONA_v1).
Execute este script uma vez para atualizar o banco de dados existente.
"""
import sqlite3
from pathlib import Path

def migrate():
    # Caminho para o banco de dados (em instance/)
    db_paths = [
        Path(__file__).parent / 'instance' / 'gestor.db',
        Path(__file__).parent / 'gestor.db'
    ]
    
    db_path = None
    for path in db_paths:
        if path.exists():
            db_path = path
            break
    
    if not db_path:
        print("⚠️ Banco de dados não encontrado!")
        print("O banco será criado automaticamente ao iniciar o app.py")
        return
    
    print(f"Conectando ao banco: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a coluna já existe
    cursor.execute("PRAGMA table_info(transacoes)")
    colunas = [row[1] for row in cursor.fetchall()]
    
    if 'subcategoria' in colunas:
        print("✅ Coluna 'subcategoria' já existe no banco de dados.")
    else:
        print("Adicionando coluna 'subcategoria'...")
        try:
            cursor.execute("ALTER TABLE transacoes ADD COLUMN subcategoria VARCHAR(50)")
            conn.commit()
            print("✅ Coluna 'subcategoria' adicionada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao adicionar coluna: {e}")
    
    conn.close()
    print("Migração concluída!")

if __name__ == "__main__":
    migrate()
