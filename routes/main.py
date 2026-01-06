"""
Blueprint para rotas principais (páginas) do GestorBot.

Este módulo contém as rotas:
- Home (/)
- Dashboard (/dashboard)
- Formulário de Receita (/receita)
- Geração de Relatório (/relatorio)
"""

import logging
from datetime import datetime, date
from io import BytesIO

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file

from config import Config
from models import get_transacoes_mes, get_totais_mes, get_gastos_por_categoria, get_receitas_por_categoria
from services.pdf_service import gerar_relatorio_mensal
from utils.auth_decorators import auth_if_enabled

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

# Nomes dos meses em português
MESES_NOMES = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]


@bp.route('/')
@auth_if_enabled
def home():
    """Renderiza a tela inicial com botões de ação."""
    return render_template('home.html')


@bp.route('/dashboard')
@auth_if_enabled
def dashboard():
    """Renderiza painel administrativo com métricas do mês."""
    try:
        hoje = date.today()
        mes = request.args.get('mes', hoje.month, type=int)
        ano = request.args.get('ano', hoje.year, type=int)
        
        aba_ativa = request.args.get('aba', 'despesas').strip().lower()
        if aba_ativa not in ['despesas', 'receitas', 'historico']:
            aba_ativa = 'despesas'
        
        per_page = request.args.get('per_page', 10, type=int)
        if per_page not in [10, 25, 50]:
            per_page = 10
        page = request.args.get('page', 1, type=int)
        if page < 1:
            page = 1
        
        # Parâmetros de busca
        busca_descricao = request.args.get('busca', '').strip()
        busca_categoria = request.args.get('categoria', '').strip()
        busca_subcategoria = request.args.get('subcategoria', '').strip()
        busca_tipo = request.args.get('tipo', '').strip()
        busca_valor_min = request.args.get('valor_min', type=float)
        busca_valor_max = request.args.get('valor_max', type=float)
        busca_data_inicio = request.args.get('data_inicio', '').strip()
        busca_data_fim = request.args.get('data_fim', '').strip()
        
        # Valida mês e ano
        if mes < 1 or mes > 12:
            mes = hoje.month
        if ano < 2000 or ano > 2100:
            ano = hoje.year
        
        # Calcula meses anterior/próximo
        mes_anterior, ano_anterior = (12, ano - 1) if mes == 1 else (mes - 1, ano)
        mes_proximo, ano_proximo = (1, ano + 1) if mes == 12 else (mes + 1, ano)
        
        # Busca dados
        totais = get_totais_mes(ano, mes)
        gastos_categoria = get_gastos_por_categoria(ano, mes)
        receitas_categoria = get_receitas_por_categoria(ano, mes)
        transacoes = get_transacoes_mes(ano, mes)
        
        # Filtra por aba
        if aba_ativa == 'despesas':
            transacoes_aba = [t for t in transacoes if t.tipo == 'DESPESA']
        elif aba_ativa == 'receitas':
            transacoes_aba = [t for t in transacoes if t.tipo == 'RECEITA']
        else:
            transacoes_aba = transacoes
        
        # Aplica filtros de busca
        transacoes_filtradas = transacoes_aba
        
        if busca_descricao:
            busca_lower = busca_descricao.lower()
            transacoes_filtradas = [
                t for t in transacoes_filtradas 
                if (t.descricao and busca_lower in t.descricao.lower()) or
                   (t.estabelecimento and busca_lower in t.estabelecimento.lower())
            ]
        
        if busca_categoria:
            transacoes_filtradas = [t for t in transacoes_filtradas if t.categoria == busca_categoria]
        
        if busca_subcategoria:
            transacoes_filtradas = [t for t in transacoes_filtradas if t.subcategoria == busca_subcategoria]
        
        if busca_tipo and busca_tipo in ['RECEITA', 'DESPESA']:
            transacoes_filtradas = [t for t in transacoes_filtradas if t.tipo == busca_tipo]
        
        if busca_valor_min is not None:
            transacoes_filtradas = [t for t in transacoes_filtradas if t.valor >= busca_valor_min]
        
        if busca_valor_max is not None:
            transacoes_filtradas = [t for t in transacoes_filtradas if t.valor <= busca_valor_max]
        
        if busca_data_inicio:
            try:
                data_inicio = datetime.strptime(busca_data_inicio, '%Y-%m-%d').date()
                transacoes_filtradas = [t for t in transacoes_filtradas if t.data and t.data >= data_inicio]
            except ValueError:
                pass
        
        if busca_data_fim:
            try:
                data_fim = datetime.strptime(busca_data_fim, '%Y-%m-%d').date()
                transacoes_filtradas = [t for t in transacoes_filtradas if t.data and t.data <= data_fim]
            except ValueError:
                pass
        
        # Ordena e pagina
        transacoes_ordenadas = sorted(transacoes_filtradas, key=lambda t: t.data if t.data else hoje, reverse=True)
        total_transacoes = len(transacoes_ordenadas)
        total_pages = max(1, (total_transacoes + per_page - 1) // per_page)
        
        if page > total_pages:
            page = total_pages
        
        start_idx = (page - 1) * per_page
        transacoes_pagina = transacoes_ordenadas[start_idx:start_idx + per_page]
        
        # Formata transações
        transacoes_recentes = []
        for t in transacoes_pagina:
            t_dict = t.to_dict()
            t_dict['data_formatada'] = t.data.strftime('%d/%m') if t.data else '-'
            transacoes_recentes.append(t_dict)
        
        # Paginação visual
        if total_pages <= 7:
            paginas_visiveis = list(range(1, total_pages + 1))
        elif page <= 4:
            paginas_visiveis = list(range(1, 6)) + ['...', total_pages]
        elif page >= total_pages - 3:
            paginas_visiveis = [1, '...'] + list(range(total_pages - 4, total_pages + 1))
        else:
            paginas_visiveis = [1, '...'] + list(range(page - 1, page + 2)) + ['...', total_pages]
        
        todas_categorias = list(Config.CATEGORIAS_DESPESA) + ['Vendas', 'PIX', 'Cartão', 'Transferência', 'Outros']
        
        dados = {
            'faturamento': totais['receitas'],
            'gastos': totais['despesas'],
            'lucro': totais['lucro'],
            'gastos_por_categoria': gastos_categoria,
            'receitas_por_categoria': receitas_categoria,
            'transacoes_recentes': transacoes_recentes,
            'total_transacoes': total_transacoes,
            'total_transacoes_aba': len(transacoes_aba),
            'total_transacoes_mes': len(transacoes),
            'mes_atual': mes,
            'ano_atual': ano,
            'mes_nome': MESES_NOMES[mes],
            'mes_anterior': mes_anterior,
            'ano_anterior': ano_anterior,
            'mes_proximo': mes_proximo,
            'ano_proximo': ano_proximo,
            'categorias': Config.CATEGORIAS_DESPESA,
            'categorias_subcategorias': Config.CATEGORIAS_SUBCATEGORIAS,
            'todas_categorias': todas_categorias,
            'aba_ativa': aba_ativa,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'paginas_visiveis': paginas_visiveis,
            'busca': busca_descricao,
            'busca_categoria': busca_categoria,
            'busca_subcategoria': busca_subcategoria,
            'busca_tipo': busca_tipo,
            'busca_valor_min': busca_valor_min,
            'busca_valor_max': busca_valor_max,
            'busca_data_inicio': busca_data_inicio,
            'busca_data_fim': busca_data_fim
        }
        
        return render_template('dashboard.html', **dados)
        
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard: {e}")
        flash('Erro ao carregar o painel.', 'error')
        return redirect(url_for('main.home'))


@bp.route('/analise-anual')
@auth_if_enabled
def analise_anual():
    """Renderiza o dashboard de análise anual."""
    from models import get_totais_ano, get_totais_mensais_ano
    
    try:
        hoje = date.today()
        ano = request.args.get('ano', hoje.year, type=int)
        
        if ano < 2000 or ano > 2100:
            ano = hoje.year
        
        # Totais do ano atual
        totais = get_totais_ano(ano)
        dados_mensais = get_totais_mensais_ano(ano)
        
        # Totais do ano anterior para comparativo
        ano_anterior = ano - 1
        totais_anterior = get_totais_ano(ano_anterior)
        dados_mensais_anterior = get_totais_mensais_ano(ano_anterior)
        
        # Calcula variações percentuais
        def calcular_variacao(atual, anterior):
            if anterior == 0:
                return None  # N/A
            return ((atual - anterior) / anterior) * 100
        
        variacao_receitas = calcular_variacao(totais['receitas'], totais_anterior['receitas'])
        variacao_despesas = calcular_variacao(totais['despesas'], totais_anterior['despesas'])
        variacao_lucro = calcular_variacao(totais['lucro'], totais_anterior['lucro']) if totais_anterior['lucro'] != 0 else None
        
        dados = {
            'ano': ano,
            'ano_anterior': ano_anterior,
            'receitas': totais['receitas'],
            'despesas': totais['despesas'],
            'lucro': totais['lucro'],
            'receitas_anterior': totais_anterior['receitas'],
            'despesas_anterior': totais_anterior['despesas'],
            'lucro_anterior': totais_anterior['lucro'],
            'variacao_receitas': variacao_receitas,
            'variacao_despesas': variacao_despesas,
            'variacao_lucro': variacao_lucro,
            'dados_mensais': dados_mensais,
            'dados_mensais_anterior': dados_mensais_anterior
        }
        
        return render_template('analise_anual.html', **dados)
        
    except Exception as e:
        logger.error(f"Erro ao carregar análise anual: {e}")
        flash('Erro ao carregar análise anual.', 'error')
        return redirect(url_for('main.dashboard'))


@bp.route('/receita')
@auth_if_enabled
def form_receita():
    """Renderiza formulário para lançar receita."""
    hoje = date.today().strftime('%Y-%m-%d')
    return render_template('receita.html', categorias=['Vendas', 'Outros'], hoje=hoje)


@bp.route('/relatorio')
@auth_if_enabled
def gerar_relatorio():
    """Gera relatório mensal em PDF para download."""
    hoje = date.today()
    mes = request.args.get('mes', hoje.month, type=int)
    ano = request.args.get('ano', hoje.year, type=int)
    tipo_filtro = request.args.get('tipo', '').upper().strip()
    
    if tipo_filtro and tipo_filtro not in ['DESPESA', 'RECEITA']:
        tipo_filtro = ''
    
    if mes < 1 or mes > 12:
        mes = hoje.month
    
    try:
        totais = get_totais_mes(ano, mes)
        gastos_categoria = get_gastos_por_categoria(ano, mes) if tipo_filtro != 'RECEITA' else {}
        receitas_categoria = get_receitas_por_categoria(ano, mes) if tipo_filtro != 'DESPESA' else {}
        transacoes = get_transacoes_mes(ano, mes)
        
        if tipo_filtro == 'DESPESA':
            transacoes = [t for t in transacoes if t.tipo == 'DESPESA']
        elif tipo_filtro == 'RECEITA':
            transacoes = [t for t in transacoes if t.tipo == 'RECEITA']
        
        transacoes_ordenadas = sorted(transacoes, key=lambda t: t.data if t.data else hoje)
        
        pdf_bytes = gerar_relatorio_mensal(
            mes=mes,
            ano=ano,
            totais=totais,
            gastos_categoria=gastos_categoria,
            receitas_categoria=receitas_categoria,
            transacoes=transacoes_ordenadas,
            tipo_filtro=tipo_filtro
        )
        
        meses_arquivo = [
            '', 'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ]
        sufixo_tipo = '_despesas' if tipo_filtro == 'DESPESA' else ('_receitas' if tipo_filtro == 'RECEITA' else '')
        filename = f"relatorio_mona{sufixo_tipo}_{meses_arquivo[mes]}_{ano}.pdf"
        
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        flash('Erro ao gerar relatório. Tente novamente.', 'error')
        return redirect(url_for('main.dashboard', mes=mes, ano=ano))


@bp.route('/exportar-csv')
@auth_if_enabled
def exportar_csv():
    """Exporta transações do mês em CSV para download."""
    from services.csv_service import gerar_csv_transacoes
    
    hoje = date.today()
    mes = request.args.get('mes', hoje.month, type=int)
    ano = request.args.get('ano', hoje.year, type=int)
    tipo_filtro = request.args.get('tipo', '').upper().strip()
    
    if tipo_filtro and tipo_filtro not in ['DESPESA', 'RECEITA']:
        tipo_filtro = ''
    
    if mes < 1 or mes > 12:
        mes = hoje.month
    
    try:
        transacoes = get_transacoes_mes(ano, mes)
        
        if tipo_filtro == 'DESPESA':
            transacoes = [t for t in transacoes if t.tipo == 'DESPESA']
        elif tipo_filtro == 'RECEITA':
            transacoes = [t for t in transacoes if t.tipo == 'RECEITA']
        
        transacoes_ordenadas = sorted(transacoes, key=lambda t: t.data if t.data else hoje)
        
        csv_bytes = gerar_csv_transacoes(transacoes_ordenadas, mes, ano)
        
        meses_arquivo = [
            '', 'janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
        ]
        sufixo_tipo = '_despesas' if tipo_filtro == 'DESPESA' else ('_receitas' if tipo_filtro == 'RECEITA' else '')
        filename = f"transacoes_mona{sufixo_tipo}_{meses_arquivo[mes]}_{ano}.csv"
        
        return send_file(
            BytesIO(csv_bytes),
            mimetype='text/csv; charset=utf-8',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Erro ao exportar CSV: {e}")
        flash('Erro ao exportar CSV. Tente novamente.', 'error')
        return redirect(url_for('main.dashboard', mes=mes, ano=ano))
