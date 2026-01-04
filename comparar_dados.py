import sqlite3
import os

# Conectar ao banco
conn = sqlite3.connect('instance/gestor.db')
cursor = conn.cursor()

# Obter URLs dos comprovantes no banco
cursor.execute("SELECT comprovante_url, valor FROM transacoes WHERE comprovante_url IS NOT NULL")
db_files = {row[0].split('/')[-1]: row[1] for row in cursor.fetchall()}

conn.close()

# Listar arquivos na pasta
folder_path = 'Comprovantes_Mona'
disk_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

print(f"Total arquivos no disco: {len(disk_files)}")
print(f"Total arquivos no banco: {len(db_files)}")

# Verificar discrepâncias
missing_in_db = []
for f in disk_files:
    # O sistema salva como 'nota_timestamp.ext', então não dá para comparar por nome diretamente
    # Mas podemos comparar por valor se os nomes foram perdidos, 
    # OU se o sistema manteve o nome original? 
    # O código app.py renomeia para nota_timestamp.
    pass

# Como os nomes mudam, vamos comparar pela SOMA dos valores.
# Vamos pegar a soma do banco e a soma calculada (eu tenho os valores extraidos no histórico/memória, mas posso somar de novo se precisar)
# O usuário disse que o sistema acusa 64430.28.
# Vou listar os valores do banco para ver se identifico padrões.

print("\nValores no Banco:")
valores_db = sorted(list(db_files.values()))
for v in valores_db:
    print(f"R$ {v:.2f}")

print(f"\nSoma total banco: R$ {sum(valores_db):.2f}")
print(f"Total de itens no banco: {len(valores_db)}")
