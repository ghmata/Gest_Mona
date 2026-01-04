"""
Script de migração para atualizar categorias existentes para a nova estrutura.
Movimenta os valores de categoria antiga para subcategoria e define a categoria principal.
"""
import sqlite3
from pathlib import Path

# Mapeamento: categoria antiga → (categoria principal, subcategoria)
MAPEAMENTO_CATEGORIAS = {
    # Insumos
    'Frutos do Mar': ('Insumos', 'Frutos do Mar'),
    'Carnes e Aves': ('Insumos', 'Carnes e Aves'),
    'Hortifruti': ('Insumos', 'Hortifruti'),
    'Laticínios': ('Insumos', 'Laticínios'),
    'Frutas': ('Insumos', 'Frutas'),
    'Alimento (Variado)': ('Insumos', 'Alimento (Variado)'),
    'Gelo': ('Insumos', 'Gelo'),
    
    # Bebidas
    'Bebidas': ('Bebidas', 'Bebidas'),
    'Cervejas': ('Bebidas', 'Cervejas'),
    'Destilados': ('Bebidas', 'Destilados'),
    'Vinhos': ('Bebidas', 'Vinhos'),
    'Energético': ('Bebidas', 'Energético'),
    
    # Operacional
    'Embalagens': ('Operacional', 'Embalagens'),
    'Limpeza': ('Operacional', 'Limpeza'),
    'Manutenção': ('Operacional', 'Manutenção'),
    'Gás': ('Operacional', 'Gás'),
    'Organização': ('Operacional', 'Organização'),
    
    # Pessoal
    'Pessoal': ('Pessoal', 'Pessoal'),
    'Pro Labore': ('Pessoal', 'Pro Labore'),
    'Salário': ('Pessoal', 'Salário'),
    'Freelancer': ('Pessoal', 'Freelancer'),
    'Gorjeta': ('Pessoal', 'Gorjeta'),
    'Venda de Férias': ('Pessoal', 'Venda de Férias'),
    
    # Infraestrutura
    'Aluguel': ('Infraestrutura', 'Aluguel'),
    'Energia': ('Infraestrutura', 'Energia'),
    'Seguros': ('Infraestrutura', 'Seguros'),
    
    # Administrativo
    'Impostos': ('Administrativo', 'Impostos'),
    'Transporte': ('Administrativo', 'Transporte'),
    
    # Marketing e Eventos
    'Eventos': ('Marketing e Eventos', 'Eventos'),
    'Marketing': ('Marketing e Eventos', 'Marketing'),
    
    # Outros
    'Outros': ('Outros', 'Outros'),
}

def migrate():
    # Caminho para o banco de dados
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
        return
    
    print(f"Conectando ao banco: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a coluna subcategoria já existe
    cursor.execute("PRAGMA table_info(transacoes)")
    colunas = [row[1] for row in cursor.fetchall()]
    
    if 'subcategoria' not in colunas:
        print("Adicionando coluna 'subcategoria'...")
        cursor.execute("ALTER TABLE transacoes ADD COLUMN subcategoria VARCHAR(50)")
        conn.commit()
        print("✅ Coluna 'subcategoria' adicionada!")
    
    # Buscar transações que precisam ser migradas
    cursor.execute("SELECT id, categoria, subcategoria FROM transacoes WHERE tipo = 'DESPESA'")
    transacoes = cursor.fetchall()
    
    print(f"\nEncontradas {len(transacoes)} transações de despesa para analisar...")
    
    migradas = 0
    nao_mapeadas = set()
    
    for id_transacao, categoria_atual, subcategoria_atual in transacoes:
        # Se já tem subcategoria definida e categoria é uma das principais, pula
        if subcategoria_atual and categoria_atual in ['Insumos', 'Bebidas', 'Operacional', 'Pessoal', 
                                                        'Infraestrutura', 'Administrativo', 'Marketing e Eventos', 'Outros']:
            continue
        
        # Verifica se a categoria atual está no mapeamento
        if categoria_atual in MAPEAMENTO_CATEGORIAS:
            nova_categoria, nova_subcategoria = MAPEAMENTO_CATEGORIAS[categoria_atual]
            
            cursor.execute("""
                UPDATE transacoes 
                SET categoria = ?, subcategoria = ?
                WHERE id = ?
            """, (nova_categoria, nova_subcategoria, id_transacao))
            
            migradas += 1
        else:
            nao_mapeadas.add(categoria_atual)
    
    conn.commit()
    print(f"\n✅ {migradas} transações migradas para a nova estrutura!")
    
    if nao_mapeadas:
        print(f"\n⚠️ Categorias não mapeadas (mantidas como estão):")
        for cat in sorted(nao_mapeadas):
            print(f"   - {cat}")
    
    # Mostrar resumo após migração
    cursor.execute("""
        SELECT categoria, COUNT(*) as total 
        FROM transacoes 
        WHERE tipo = 'DESPESA'
        GROUP BY categoria 
        ORDER BY total DESC
    """)
    print("\n📊 Resumo das categorias após migração:")
    for cat, total in cursor.fetchall():
        print(f"   {cat}: {total} transações")
    
    conn.close()
    print("\n✅ Migração concluída!")

if __name__ == "__main__":
    migrate()
