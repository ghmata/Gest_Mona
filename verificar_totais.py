import sqlite3

conn = sqlite3.connect('instance/gestor.db')
cursor = conn.cursor()

# Total de despesas
cursor.execute("SELECT SUM(valor), COUNT(*) FROM transacoes WHERE tipo = 'DESPESA'")
despesas = cursor.fetchone()

# Total de receitas
cursor.execute("SELECT SUM(valor), COUNT(*) FROM transacoes WHERE tipo = 'RECEITA'")
receitas = cursor.fetchone()

# Todas transações
# Todas transições
cursor.execute("SELECT id, data, valor, comprovante_url FROM transacoes ORDER BY data DESC")
transacoes = cursor.fetchall()

print("=" * 50)
print("RESUMO FINANCEIRO")
print("=" * 50)
print(f"Total DESPESAS: R$ {despesas[0] or 0:.2f} ({despesas[1] or 0} transações)")
print(f"Total RECEITAS: R$ {receitas[0] or 0:.2f} ({receitas[1] or 0} transações)")
print("=" * 50)
print("\nARQUIVOS PROCESSADOS NO BANCO:")
print("-" * 50)
for t in transacoes:
    # Extrair apenas o nome do arquivo da URL se existir
    arquivo = t[3].split('/')[-1] if t[3] else "SEM_ARQUIVO"
    print(f"ID: {t[0]} | R$ {t[2]:>10.2f} | {arquivo}")

conn.close()
