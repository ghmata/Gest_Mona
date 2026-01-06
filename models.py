"""
Módulo de modelos de dados do GestorBot.

Este módulo define os modelos SQLAlchemy para persistência de dados,
incluindo o modelo principal de Transação e funções auxiliares para
consultas e agregações.
"""

# 1. Bibliotecas padrão
from datetime import datetime
from typing import Optional
import logging

# 2. Bibliotecas externas
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Configuração de logging
logger = logging.getLogger(__name__)

# Instância do SQLAlchemy
db = SQLAlchemy()


class User(db.Model, UserMixin):
    """
    Modelo de usuário para autenticação.
    
    Attributes:
        id: Identificador único do usuário
        email: Email único usado como login
        password_hash: Hash da senha (nunca armazena senha em texto)
        nome: Nome de exibição do usuário
        role: Papel do usuário ('admin' ou 'user')
        ativo: Se o usuário pode fazer login
        created_at: Data de criação da conta
        last_login: Último acesso ao sistema
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin' ou 'user'
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'
    
    def set_password(self, password: str) -> None:
        """Hash da senha usando Werkzeug."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verifica senha contra hash armazenado."""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self) -> bool:
        """Verifica se usuário tem role de administrador."""
        return self.role == 'admin'
    
    def to_dict(self) -> dict:
        """Converte usuário para dicionário (sem senha)."""
        return {
            'id': self.id,
            'email': self.email,
            'nome': self.nome,
            'role': self.role,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Transacao(db.Model):
    """
    Modelo para representar transações financeiras (receitas e despesas).
    
    Esta classe mapeia a tabela 'transacoes' no banco de dados e armazena
    todas as informações relevantes sobre movimentações financeiras do
    restaurante.
    
    Attributes:
        id: Identificador único da transação
        tipo: Tipo da transação ('DESPESA' ou 'RECEITA')
        valor: Valor monetário da transação
        data: Data e hora da transação
        categoria: Categoria da transação
        descricao: Descrição opcional da transação
        estabelecimento: Nome do estabelecimento (para despesas)
        comprovante_url: URL do comprovante/nota fiscal
        status: Status da transação ('CONFIRMADO', 'PENDENTE', etc.)
        created_at: Data e hora de criação do registro
    """
    
    __tablename__ = 'transacoes'
    
    # Campos obrigatórios
    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo: str = db.Column(db.String(10), nullable=False)  # 'DESPESA' ou 'RECEITA'
    valor: float = db.Column(db.Float, nullable=False)
    data: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    categoria: str = db.Column(db.String(50), nullable=False)
    
    # Campos opcionais
    subcategoria: Optional[str] = db.Column(db.String(50), nullable=True)  # Subcategoria da transação
    descricao: Optional[str] = db.Column(db.String(200), nullable=True)
    estabelecimento: Optional[str] = db.Column(db.String(100), nullable=True)
    comprovante_url: Optional[str] = db.Column(db.String(500), nullable=True)
    
    # Campos de controle
    status: str = db.Column(db.String(20), default='CONFIRMADO')
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        """Representação em string do objeto Transacao."""
        return f'<Transacao {self.id}: {self.tipo} R${self.valor:.2f}>'
    
    def to_dict(self) -> dict:
        """
        Converte a transação para um dicionário.
        
        Útil para serialização JSON e envio de dados para o frontend.
        
        Returns:
            dict: Dicionário com todos os campos da transação
        
        Example:
            >>> transacao = Transacao(tipo='DESPESA', valor=150.0, ...)
            >>> dados = transacao.to_dict()
            >>> print(dados['valor'])
            150.0
        """
        return {
            'id': self.id,
            'tipo': self.tipo,
            'valor': self.valor,
            'data': self.data.isoformat() if self.data else None,
            'categoria': self.categoria,
            'subcategoria': self.subcategoria,
            'descricao': self.descricao,
            'estabelecimento': self.estabelecimento,
            'comprovante_url': self.comprovante_url,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def get_transacoes_mes(ano: int, mes: int) -> list:
    """
    Obtém todas as transações de um mês específico.
    
    Args:
        ano: Ano desejado (ex: 2024)
        mes: Mês desejado (1-12)
    
    Returns:
        list: Lista de objetos Transacao do mês especificado,
              ordenados por data decrescente
    
    Example:
        >>> transacoes = get_transacoes_mes(2024, 12)
        >>> for t in transacoes:
        ...     print(f"{t.data}: {t.valor}")
    """
    try:
        # Define o primeiro e último dia do mês
        data_inicio = datetime(ano, mes, 1)
        
        # Calcula o próximo mês para o limite superior
        if mes == 12:
            data_fim = datetime(ano + 1, 1, 1)
        else:
            data_fim = datetime(ano, mes + 1, 1)
        
        # Consulta as transações no intervalo
        transacoes = Transacao.query.filter(
            Transacao.data >= data_inicio,
            Transacao.data < data_fim
        ).order_by(Transacao.data.desc()).all()
        
        logger.info(f"Encontradas {len(transacoes)} transações para {mes}/{ano}")
        return transacoes
    
    except Exception as e:
        logger.error(f"Erro ao buscar transações do mês {mes}/{ano}: {e}")
        return []


def get_totais_mes(ano: int, mes: int) -> dict:
    """
    Calcula os totais financeiros de um mês específico.
    
    Args:
        ano: Ano desejado (ex: 2024)
        mes: Mês desejado (1-12)
    
    Returns:
        dict: Dicionário com as chaves:
            - receitas: Total de receitas do mês
            - despesas: Total de despesas do mês
            - lucro: Diferença entre receitas e despesas
    
    Example:
        >>> totais = get_totais_mes(2024, 12)
        >>> print(f"Lucro: R${totais['lucro']:.2f}")
    """
    try:
        transacoes = get_transacoes_mes(ano, mes)
        
        receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
        despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
        lucro = receitas - despesas
        
        logger.info(
            f"Totais {mes}/{ano} - Receitas: R${receitas:.2f}, "
            f"Despesas: R${despesas:.2f}, Lucro: R${lucro:.2f}"
        )
        
        return {
            'receitas': receitas,
            'despesas': despesas,
            'lucro': lucro
        }
    
    except Exception as e:
        logger.error(f"Erro ao calcular totais do mês {mes}/{ano}: {e}")
        return {
            'receitas': 0.0,
            'despesas': 0.0,
            'lucro': 0.0
        }


def get_gastos_por_categoria(ano: int, mes: int) -> dict:
    """
    Agrupa as despesas por categoria para um mês específico.
    
    Útil para gerar gráficos de pizza e análises de gastos.
    
    Args:
        ano: Ano desejado (ex: 2024)
        mes: Mês desejado (1-12)
    
    Returns:
        dict: Dicionário onde as chaves são as categorias e os valores
              são os totais gastos em cada categoria
    
    Example:
        >>> gastos = get_gastos_por_categoria(2024, 12)
        >>> for categoria, valor in gastos.items():
        ...     print(f"{categoria}: R${valor:.2f}")
    """
    try:
        transacoes = get_transacoes_mes(ano, mes)
        
        # Filtra apenas despesas
        despesas = [t for t in transacoes if t.tipo == 'DESPESA']
        
        # Agrupa por categoria
        gastos_categoria: dict = {}
        for transacao in despesas:
            categoria = transacao.categoria
            if categoria in gastos_categoria:
                gastos_categoria[categoria] += transacao.valor
            else:
                gastos_categoria[categoria] = transacao.valor
        
        logger.info(
            f"Gastos por categoria {mes}/{ano}: {len(gastos_categoria)} categorias"
        )
        
        return gastos_categoria
    
    except Exception as e:
        logger.error(f"Erro ao agrupar gastos por categoria {mes}/{ano}: {e}")
        return {}


def get_receitas_por_categoria(ano: int, mes: int) -> dict:
    """
    Agrupa as receitas por categoria (tipo de pagamento) para um mês específico.
    
    Args:
        ano: Ano desejado (ex: 2024)
        mes: Mês desejado (1-12)
    
    Returns:
        dict: Dicionário onde as chaves são as categorias (PIX, Cartão, etc.)
              e os valores são os totais recebidos em cada categoria
    """
    try:
        transacoes = get_transacoes_mes(ano, mes)
        
        # Filtra apenas receitas
        receitas = [t for t in transacoes if t.tipo == 'RECEITA']
        
        # Agrupa por categoria
        receitas_categoria: dict = {}
        for transacao in receitas:
            categoria = transacao.categoria
            if categoria in receitas_categoria:
                receitas_categoria[categoria] += transacao.valor
            else:
                receitas_categoria[categoria] = transacao.valor
        
        logger.info(
            f"Receitas por categoria {mes}/{ano}: {len(receitas_categoria)} categorias"
        )
        
        return receitas_categoria
    
    except Exception as e:
        logger.error(f"Erro ao agrupar receitas por categoria {mes}/{ano}: {e}")
        return {}


def get_gastos_por_subcategoria(ano: int, mes: int, categoria: str) -> dict:
    """
    Agrupa as despesas por subcategoria para uma categoria específica.
    
    Útil para gerar mini dashboards de detalhamento por categoria.
    
    Args:
        ano: Ano desejado (ex: 2024)
        mes: Mês desejado (1-12)
        categoria: Categoria principal para filtrar
    
    Returns:
        dict: Dicionário onde as chaves são as subcategorias e os valores
              são os totais gastos em cada subcategoria
    
    Example:
        >>> gastos = get_gastos_por_subcategoria(2024, 12, 'Insumos')
        >>> for subcat, valor in gastos.items():
        ...     print(f"{subcat}: R${valor:.2f}")
    """
    try:
        transacoes = get_transacoes_mes(ano, mes)
        
        # Filtra despesas da categoria especificada
        despesas = [t for t in transacoes if t.tipo == 'DESPESA' and t.categoria == categoria]
        
        # Agrupa por subcategoria
        gastos_subcategoria: dict = {}
        for transacao in despesas:
            subcategoria = transacao.subcategoria or 'Sem subcategoria'
            if subcategoria in gastos_subcategoria:
                gastos_subcategoria[subcategoria] += transacao.valor
            else:
                gastos_subcategoria[subcategoria] = transacao.valor
        
        logger.info(
            f"Gastos por subcategoria {categoria} {mes}/{ano}: {len(gastos_subcategoria)} subcategorias"
        )
        
        return gastos_subcategoria
    
    except Exception as e:
        logger.error(f"Erro ao agrupar gastos por subcategoria {mes}/{ano}: {e}")
        return {}


def get_totais_diarios_mes(ano: int, mes: int) -> dict:
    """
    Calcula totais diários para o gráfico de evolução (Dias x Valores).
    
    Args:
        ano: Ano desejado
        mes: Mês desejado
    
    Returns:
        dict: {
            'dias': [1, 2, ...], 
            'receitas': [0.0, ...], 
            'despesas': [0.0, ...]
        }
    """
    try:
        from calendar import monthrange
        
        # Determina quantos dias tem o mês
        _, num_dias = monthrange(ano, mes)
        
        # Inicializa estruturas
        dias = list(range(1, num_dias + 1))
        # Dicionários para acesso rápido: {dia: valor}
        receitas_map = {d: 0.0 for d in dias}
        despesas_map = {d: 0.0 for d in dias}
        
        # Busca transações
        transacoes = get_transacoes_mes(ano, mes)
        
        for t in transacoes:
            dia = t.data.day
            if t.tipo == 'RECEITA':
                receitas_map[dia] += t.valor
            elif t.tipo == 'DESPESA':
                despesas_map[dia] += t.valor
        
        # Converte para listas ordenadas (para o Chart.js)
        # Atenção: Retorna listas alinhadas pelo índice
        resultado = {
            'dias': dias,
            'receitas': [receitas_map[d] for d in dias],
            'despesas': [despesas_map[d] for d in dias]
        }
        
        logger.info(f"Dados diários processados para {mes}/{ano}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao calcular totais diários: {e}")
        return {'dias': [], 'receitas': [], 'despesas': []}


def get_totais_ano(ano: int) -> dict:
    """
    Calcula os totais financeiros de um ano inteiro.
    
    Args:
        ano: Ano desejado (ex: 2024)
    
    Returns:
        dict: Dicionário com as chaves:
            - receitas: Soma de todas as receitas do ano
            - despesas: Soma de todas as despesas do ano
            - lucro: Diferença entre receitas e despesas
    """
    try:
        inicio_ano = datetime(ano, 1, 1)
        fim_ano = datetime(ano, 12, 31, 23, 59, 59)
        
        transacoes = Transacao.query.filter(
            Transacao.data >= inicio_ano,
            Transacao.data <= fim_ano,
            Transacao.status == 'CONFIRMADO'
        ).all()
        
        receitas = sum(t.valor for t in transacoes if t.tipo == 'RECEITA')
        despesas = sum(t.valor for t in transacoes if t.tipo == 'DESPESA')
        
        resultado = {
            'receitas': receitas,
            'despesas': despesas,
            'lucro': receitas - despesas
        }
        
        logger.info(f"Totais anuais {ano}: R={receitas:.2f}, D={despesas:.2f}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao calcular totais anuais {ano}: {e}")
        return {'receitas': 0.0, 'despesas': 0.0, 'lucro': 0.0}


def get_totais_mensais_ano(ano: int) -> dict:
    """
    Calcula totais mensais para gráfico de evolução anual (Meses x Valores).
    
    Args:
        ano: Ano desejado
    
    Returns:
        dict: {
            'meses': ['Jan', 'Fev', ...],
            'receitas': [0.0, ...],
            'despesas': [0.0, ...]
        }
    """
    try:
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        receitas_mes = [0.0] * 12
        despesas_mes = [0.0] * 12
        
        # Busca todas as transações do ano
        inicio_ano = datetime(ano, 1, 1)
        fim_ano = datetime(ano, 12, 31, 23, 59, 59)
        
        transacoes = Transacao.query.filter(
            Transacao.data >= inicio_ano,
            Transacao.data <= fim_ano,
            Transacao.status == 'CONFIRMADO'
        ).all()
        
        for t in transacoes:
            mes_idx = t.data.month - 1  # 0-indexed
            if t.tipo == 'RECEITA':
                receitas_mes[mes_idx] += t.valor
            elif t.tipo == 'DESPESA':
                despesas_mes[mes_idx] += t.valor
        
        resultado = {
            'meses': meses_nomes,
            'receitas': receitas_mes,
            'despesas': despesas_mes
        }
        
        logger.info(f"Dados mensais processados para {ano}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao calcular totais mensais do ano {ano}: {e}")
        return {'meses': [], 'receitas': [], 'despesas': []}
