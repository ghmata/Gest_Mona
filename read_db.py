import sqlite3

conn = sqlite3.connect('instance/database_att.db')
cursor = conn.cursor()

# Listar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cursor.fetchall()
print("=== TABELAS ===")
for t in tabelas:
    print(f"- {t[0]}")

# Estrutura da tabela transacoes
print("\n\n=== ESTRUTURA TRANSACOES ===")
cursor.execute("PRAGMA table_info(transacoes)")
colunas = cursor.fetchall()
for c in colunas:
    print(f"  {c[1]} ({c[2]})")

# Contagem
cursor.execute("SELECT COUNT(*) FROM transacoes")
print(f"\nTotal de transações: {cursor.fetchone()[0]}")

# Amostra de dados
print("\n=== AMOSTRA DE DADOS (5 primeiros) ===")
cursor.execute("SELECT id, tipo, valor, data, categoria, subcategoria FROM transacoes LIMIT 5")
for r in cursor.fetchall():
    print(f"  ID={r[0]}, Tipo={r[1]}, Valor={r[2]}, Data={r[3]}, Cat={r[4]}, Subcat={r[5]}")

# Estrutura da tabela users se existir
print("\n\n=== ESTRUTURA USERS ===")
cursor.execute("PRAGMA table_info(users)")
colunas = cursor.fetchall()
for c in colunas:
    print(f"  {c[1]} ({c[2]})")

cursor.execute("SELECT COUNT(*) FROM users")
print(f"\nTotal de usuários: {cursor.fetchone()[0]}")

conn.close()

