"""Script de teste para geração de PDF."""
from app import app
from models import get_totais_mes, get_gastos_por_categoria, get_receitas_por_categoria, get_transacoes_mes
from services.pdf_service import gerar_relatorio_mensal

with app.app_context():
    mes, ano = 12, 2025
    
    print("Buscando dados...")
    totais = get_totais_mes(ano, mes)
    print(f"Totais: {totais}")
    
    gastos = get_gastos_por_categoria(ano, mes)
    print(f"Despesas: {len(gastos)} categorias")
    
    receitas = get_receitas_por_categoria(ano, mes)
    print(f"Receitas: {len(receitas)} categorias")
    
    transacoes = get_transacoes_mes(ano, mes)
    print(f"Transacoes: {len(transacoes)}")
    
    print("\nGerando PDF...")
    try:
        pdf = gerar_relatorio_mensal(mes, ano, totais, gastos, receitas, transacoes)
        print(f"PDF gerado: {len(pdf)} bytes")
        
        with open('teste_relatorio.pdf', 'wb') as f:
            f.write(pdf)
        print("Arquivo salvo: teste_relatorio.pdf")
    except Exception as e:
        print(f"ERRO: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
