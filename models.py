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

# Configuração de logging
logger = logging.getLogger(__name__)

# Instância do SQLAlchemy
db = SQLAlchemy()


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
