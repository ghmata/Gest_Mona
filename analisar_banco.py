"""
Script para migrar dados do banco gestor_atualizado.db para o formato atual
"""
import sqlite3
import shutil
from datetime import datetime

# 1. Analisar estrutura do banco fonte
print("=" * 60)
print("ANÁLISE DO BANCO FONTE (gestor_atualizado.db)")
print("=" * 60)

conn_fonte = sqlite3.connect('instance/gestor_atualizado.db')
cursor_fonte = conn_fonte.cursor()

# Estrutura
cursor_fonte.execute("PRAGMA table_info(transacoes)")
colunas_fonte = cursor_fonte.fetchall()
print("\nColunas:")
for c in colunas_fonte:
    print(f"  {c[0]}. {c[1]} ({c[2]}) {'NOT NULL' if c[3] else ''} default={c[4]}")

# Total
cursor_fonte.execute("SELECT COUNT(*) FROM transacoes")
total = cursor_fonte.fetchone()[0]
print(f"\nTotal de registros: {total}")

# Amostra
cursor_fonte.execute("SELECT * FROM transacoes ORDER BY id DESC LIMIT 5")
print("\nÚltimos 5 registros:")
for row in cursor_fonte.fetchall():
    print(f"  {row}")

# Verificar se tem subcategoria
nomes_colunas = [c[1] for c in colunas_fonte]
print(f"\nColunas existentes: {nomes_colunas}")
print(f"Tem subcategoria: {'subcategoria' in nomes_colunas}")

conn_fonte.close()

print("\n" + "=" * 60)
print("PRÓXIMO PASSO:")
print("=" * 60)
print("""
Para usar este banco no sistema:
1. Fazer backup do gestor.db atual
2. Renomear gestor_atualizado.db para gestor.db
   OU
   Copiar dados de gestor_atualizado.db para gestor.db

Deseja prosseguir? Execute o script migrar_banco_real.py
""")
