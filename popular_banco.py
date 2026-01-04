"""
Script para popular banco de dados com dados fake para teste.
Cria transações de outubro/2024 a fevereiro/2025 com todas as categorias.
"""

from datetime import datetime, timedelta
import random
from app import app, db
from models import Transacao

# Categorias de DESPESA do MONA Beach Club
CATEGORIAS_DESPESA = [
    'Frutos do Mar',
    'Carnes e Aves',
    'Hortifruti',
    'Bebidas',
    'Cervejas',
    'Destilados',
    'Vinhos',
    'Laticínios',
    'Embalagens',
    'Limpeza',
    'Manutenção',
    'Gás',
    'Outros'
]

# Categorias de RECEITA (tipos de pagamento)
CATEGORIAS_RECEITA = [
    'Vendas',
    'PIX',
    'Cartão',
    'Transferência',
    'Outros'
]

# Fornecedores fictícios para cada categoria
FORNECEDORES = {
    'Frutos do Mar': ['Pescados Floripa', 'Mar Azul Pescados', 'Camarão Lagoa'],
    'Carnes e Aves': ['Frigorífico SC', 'Carnes Premium', 'Aves Santa Catarina'],
    'Hortifruti': ['Ceasa Floripa', 'Verde Vida', 'Horta Orgânica'],
    'Bebidas': ['Coca-Cola', 'Ambev Sucos', 'Red Bull Brasil'],
    'Cervejas': ['Ambev', 'Heineken Brasil', 'Corona Distribuidora'],
    'Destilados': ['Diageo', 'Pernod Ricard', 'Casa Beefeater'],
    'Vinhos': ['Perrier-Jouët', 'Wine Shop', 'Champagne House'],
    'Laticínios': ['Tirol', 'Laticínios Holandês', 'Queijaria Artesanal'],
    'Embalagens': ['Embalax', 'Descart Plus', 'PlastiPack'],
    'Limpeza': ['Ypê', 'Start Química', 'Clean Pro'],
    'Manutenção': ['Manutenção Geral', 'Elétrica SC', 'Refrigeração Sul'],
    'Gás': ['Ultragaz', 'Liquigás', 'Copagaz'],
    'Outros': ['Diversos', 'Material Escritório', 'Correios']
}

# Faixas de valores por categoria (min, max)
VALORES_DESPESA = {
    'Frutos do Mar': (800, 3500),
    'Carnes e Aves': (600, 2500),
    'Hortifruti': (300, 1200),
    'Bebidas': (400, 1500),
    'Cervejas': (1000, 4000),
    'Destilados': (1500, 6000),
    'Vinhos': (2000, 8000),
    'Laticínios': (200, 800),
    'Embalagens': (150, 600),
    'Limpeza': (100, 400),
    'Manutenção': (200, 1500),
    'Gás': (300, 800),
    'Outros': (50, 500)
}

# Faixas de valores por tipo de receita
VALORES_RECEITA = {
    'Vendas': (3000, 15000),  # Caixa do dia
    'PIX': (500, 5000),
    'Cartão': (2000, 12000),
    'Transferência': (1000, 8000),
    'Outros': (100, 1000)
}


def gerar_data_aleatoria(ano: int, mes: int) -> datetime:
    """Gera uma data aleatória dentro do mês especificado."""
    if mes == 2:
        max_dia = 28
    elif mes in [4, 6, 9, 11]:
        max_dia = 30
    else:
        max_dia = 31
    
    dia = random.randint(1, max_dia)
    hora = random.randint(8, 22)
    minuto = random.randint(0, 59)
    
    return datetime(ano, mes, dia, hora, minuto)


def criar_despesas(ano: int, mes: int, qtd_por_categoria: int = 3):
    """Cria despesas para um mês específico."""
    transacoes = []
    
    for categoria in CATEGORIAS_DESPESA:
        # Número aleatório de transações por categoria (1 a qtd_por_categoria)
        num_transacoes = random.randint(1, qtd_por_categoria)
        
        for _ in range(num_transacoes):
            min_val, max_val = VALORES_DESPESA[categoria]
            valor = round(random.uniform(min_val, max_val), 2)
            fornecedor = random.choice(FORNECEDORES[categoria])
            
            transacao = Transacao(
                tipo='DESPESA',
                valor=valor,
                data=gerar_data_aleatoria(ano, mes),
                categoria=categoria,
                estabelecimento=fornecedor,
                descricao=f'Compra {categoria.lower()}'
            )
            transacoes.append(transacao)
    
    return transacoes


def criar_receitas(ano: int, mes: int, qtd_por_categoria: int = 5):
    """Cria receitas para um mês específico."""
    transacoes = []
    
    for categoria in CATEGORIAS_RECEITA:
        # Número aleatório de transações por categoria
        if categoria == 'Vendas':
            # Mais vendas em caixa (quase todo dia)
            num_transacoes = random.randint(15, 25)
        elif categoria in ['PIX', 'Cartão']:
            num_transacoes = random.randint(5, 12)
        else:
            num_transacoes = random.randint(1, 4)
        
        for _ in range(num_transacoes):
            min_val, max_val = VALORES_RECEITA[categoria]
            valor = round(random.uniform(min_val, max_val), 2)
            
            transacao = Transacao(
                tipo='RECEITA',
                valor=valor,
                data=gerar_data_aleatoria(ano, mes),
                categoria=categoria,
                descricao=f'Receita {categoria}'
            )
            transacoes.append(transacao)
    
    return transacoes


def popular_banco():
    """Popula o banco com dados de outubro/2024 a fevereiro/2025."""
    
    # Meses a criar: Out/2025, Nov/2025, Dez/2025, Jan/2026, Fev/2026
    meses = [
        (2025, 10),
        (2025, 11),
        (2025, 12),
        (2026, 1),
        (2026, 2)
    ]
    
    with app.app_context():
        # Limpa banco existente
        print("🗑️  Limpando banco de dados...")
        Transacao.query.delete()
        db.session.commit()
        
        total = 0
        
        for ano, mes in meses:
            print(f"\n📅 Criando dados para {mes:02d}/{ano}...")
            
            # Cria despesas
            despesas = criar_despesas(ano, mes)
            for d in despesas:
                db.session.add(d)
            print(f"   ➖ {len(despesas)} despesas criadas")
            
            # Cria receitas
            receitas = criar_receitas(ano, mes)
            for r in receitas:
                db.session.add(r)
            print(f"   ➕ {len(receitas)} receitas criadas")
            
            total += len(despesas) + len(receitas)
        
        db.session.commit()
        
        print(f"\n✅ Banco populado com {total} transações!")
        print("\n📊 Resumo por mês:")
        
        for ano, mes in meses:
            transacoes = Transacao.query.filter(
                db.extract('year', Transacao.data) == ano,
                db.extract('month', Transacao.data) == mes
            ).all()
            
            receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
            despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
            lucro = receitas - despesas
            
            print(f"   {mes:02d}/{ano}: {len(transacoes)} transações | "
                  f"Receita: R${receitas:,.2f} | Despesas: R${despesas:,.2f} | "
                  f"Lucro: R${lucro:,.2f}")


if __name__ == '__main__':
    popular_banco()
