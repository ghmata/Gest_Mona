"""
Script para migrar o banco de dados real do restaurante MONA
Faz backup, substitui o banco e adiciona coluna subcategoria se necessário
"""
import sqlite3
import shutil
import os
from datetime import datetime

# Caminhos
BANCO_ATUAL = 'instance/gestor.db'
BANCO_NOVO = 'instance/gestor_atualizado.db'
BACKUP_DIR = 'instance/backups'

def main():
    print("=" * 60)
    print("MIGRAÇÃO DO BANCO DE DADOS MONA")
    print("=" * 60)
    
    # 1. Criar diretório de backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 2. Backup do banco atual
    if os.path.exists(BANCO_ATUAL):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'{BACKUP_DIR}/gestor_backup_{timestamp}.db'
        shutil.copy2(BANCO_ATUAL, backup_path)
        print(f"✅ Backup criado: {backup_path}")
    else:
        print("⚠️ Banco atual não encontrado, será criado novo")
    
    # 3. Verificar se o banco novo existe
    if not os.path.exists(BANCO_NOVO):
        print(f"❌ Erro: {BANCO_NOVO} não encontrado!")
        return
    
    # 4. Substituir banco atual pelo novo
    shutil.copy2(BANCO_NOVO, BANCO_ATUAL)
    print(f"✅ Banco substituído: {BANCO_NOVO} -> {BANCO_ATUAL}")
    
    # 5. Verificar/adicionar coluna subcategoria
    conn = sqlite3.connect(BANCO_ATUAL)
    cursor = conn.cursor()
    
    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(transacoes)")
    colunas = [c[1] for c in cursor.fetchall()]
    print(f"\n📋 Colunas atuais: {colunas}")
    
    if 'subcategoria' not in colunas:
        print("\n🔧 Adicionando coluna 'subcategoria'...")
        cursor.execute("ALTER TABLE transacoes ADD COLUMN subcategoria TEXT")
        conn.commit()
        print("✅ Coluna 'subcategoria' adicionada!")
    else:
        print("✅ Coluna 'subcategoria' já existe")
    
    # 6. Estatísticas
    cursor.execute("SELECT COUNT(*) FROM transacoes")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT tipo, COUNT(*) FROM transacoes GROUP BY tipo")
    por_tipo = cursor.fetchall()
    
    print(f"\n📊 Estatísticas:")
    print(f"   Total de transações: {total}")
    for tipo, count in por_tipo:
        print(f"   - {tipo}: {count}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Reinicie a aplicação Flask")
    print("2. Acesse o dashboard para verificar os dados")

if __name__ == '__main__':
    main()
