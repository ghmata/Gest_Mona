"""
Módulo de configurações centralizadas do GestorBot.

Este módulo contém todas as configurações necessárias para o funcionamento
da aplicação, incluindo configurações do Flask, banco de dados, upload de
arquivos e integração com a API Groq.
"""

# 1. Bibliotecas padrão
import os
import logging
import secrets
from pathlib import Path

# 2. Bibliotecas externas
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
# Carrega variáveis de ambiente do arquivo .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """
    Classe de configuração centralizada para a aplicação GestorBot.
    
    Todas as configurações são carregadas de variáveis de ambiente
    quando disponíveis, com valores padrão seguros para desenvolvimento.
    
    Attributes:
        SECRET_KEY: Chave secreta para sessões Flask
        SQLALCHEMY_DATABASE_URI: URI de conexão com o banco de dados
        SQLALCHEMY_TRACK_MODIFICATIONS: Desabilita rastreamento de modificações
        UPLOAD_FOLDER: Caminho absoluto para pasta de uploads
        MAX_CONTENT_LENGTH: Tamanho máximo de upload (16MB)
        ALLOWED_EXTENSIONS: Extensões de arquivo permitidas
        GROQ_API_KEY: Chave da API Groq para OCR
        GROQ_MODEL: Modelo de visão da Groq a ser utilizado
        CATEGORIAS_DESPESA: Lista de categorias de despesas disponíveis
    """
    
    # Diretório base do projeto
    BASE_DIR: Path = Path(__file__).resolve().parent
    
    # Configurações do Flask
    # SECRET_KEY: carrega do .env ou gera uma chave segura automaticamente
    SECRET_KEY: str = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    
    # Configurações do banco de dados SQLite
    # Banco de dados armazenado em /instance/ (convenção Flask)
    INSTANCE_DIR: Path = BASE_DIR / 'instance'
    SQLALCHEMY_DATABASE_URI: str = f'sqlite:///{INSTANCE_DIR / "gestor.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
    # Configurações de upload de arquivos
    UPLOAD_FOLDER: Path = BASE_DIR / 'static' / 'uploads'
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB em bytes
    ALLOWED_EXTENSIONS: set = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
    
    # Configurações da API Groq
    GROQ_API_KEY: str = os.getenv('GROQ_API_KEY', '')
    # Modelo com suporte a visão (imagens)
    # Opções: meta-llama/llama-4-maverick-17b-128e-instruct ou meta-llama/llama-4-scout-17b-16e-instruct
    GROQ_MODEL: str = 'meta-llama/llama-4-maverick-17b-128e-instruct'
    
    # Senha de segurança para exclusão de transações
    # Altere para uma senha personalizada via .env ou aqui diretamente
    SENHA_EXCLUSAO: str = os.getenv('SENHA_EXCLUSAO', 'mona2026')
    
    # Categorias de despesas para MONA Beach Club Joaquina
    # Estrutura hierárquica: Categoria Principal → Subcategorias
    CATEGORIAS_SUBCATEGORIAS: dict = {
        'Insumos': [
            'Frutos do Mar',      # Camarão, peixe, salmão, polvo, ostras, lula
            'Carnes e Aves',      # Carne bovina, frango, hambúrguer
            'Hortifruti',         # Legumes, verduras, saladas
            'Laticínios',         # Queijos, manteiga, creme de leite
            'Frutas',             # Frutas diversas
            'Alimento (Variado)', # Alimentos diversos não classificados
            'Gelo',               # Gelo para bebidas e conservação
            'Outros'
        ],
        'Bebidas': [
            'Bebidas',            # Água, refrigerantes, sucos, café
            'Cervejas',           # Budweiser, Heineken, Stella, Corona, etc.
            'Destilados',         # Gin, vodka, whisky, rum, tequila (drinks)
            'Vinhos',             # Champagnes, espumantes, vinhos
            'Energético',         # Red Bull, Monster, etc.
            'Outros'
        ],
        'Operacional': [
            'Embalagens',         # Descartáveis, guardanapos, sacolas
            'Limpeza',            # Produtos de limpeza, higiene
            'Manutenção',         # Reparos, equipamentos, peças
            'Gás',                # Gás de cozinha
            'Organização',        # Serviços administrativos e organização
            'Outros'
        ],
        'Pessoal': [
            'Pessoal',            # Folha de pagamento geral, FGTS, INSS
            'Pro Labore',         # Retirada dos sócios
            'Salário',            # Salários específicos
            'Freelancer',         # Pagamentos a terceiros
            'Gorjeta',            # Gorjetas e gratificações
            'Venda de Férias',    # Venda de férias de funcionários
            'Venda de Folga',     # Venda de folga de funcionários
            'Vale Transporte',    # VT - Vale transporte
            'Vale Refeição',      # VR - Vale refeição
            'DJ/Músicos',   # Contratação de DJ/Banda/Músicos
            'Hora Extra',   # Pagamento de horas extras
            'Outros'
        ],
        'Infraestrutura': [
            'Aluguel',            # Aluguel de imóvel, equipamentos
            'Energia',            # Conta de luz, água, gás encanado
            'Seguros',            # Seguros em geral
            'Outros'
        ],
        'Administrativo': [
            'Impostos',           # Taxas, alvarás, DAS, tarifas bancárias
            'Transporte',         # Combustível, fretes, Uber, táxi
            'Outros'
        ],
        'Marketing e Eventos': [
            'Eventos',            # Festas, confraternizações, shows
            'Marketing',          # Publicidade, redes sociais, anúncios
            'Aluguel',            # Aluguel de espaço para eventos
            'Outros'
        ],
        'Outros': [
            'Outros'              # Qualquer item não classificado
        ]
    }
    
    # Lista de categorias principais (para compatibilidade)
    CATEGORIAS_PRINCIPAIS: list = list(CATEGORIAS_SUBCATEGORIAS.keys())
    
    # Lista de todas as subcategorias (para validação e compatibilidade)
    # Gera dinamicamente a partir do dicionário
    @classmethod
    def get_todas_subcategorias(cls) -> list:
        """Retorna lista única de todas as subcategorias."""
        todas = set()
        for subcats in cls.CATEGORIAS_SUBCATEGORIAS.values():
            todas.update(subcats)
        return sorted(list(todas))
    
    # CATEGORIAS_DESPESA mantida para compatibilidade com código existente
    # Agora contém as categorias principais
    CATEGORIAS_DESPESA: list = list(CATEGORIAS_SUBCATEGORIAS.keys())
    
    @classmethod
    def verificar_configuracoes(cls) -> bool:
        """
        Verifica se todas as configurações obrigatórias estão definidas.
        
        Esta função valida a presença da chave da API Groq, que é necessária
        para o funcionamento do OCR de notas fiscais.
        
        Returns:
            bool: True se todas as configurações estão válidas, False caso contrário
        
        Raises:
            Não levanta exceções, apenas loga avisos para configurações ausentes.
        
        Example:
            >>> if Config.verificar_configuracoes():
            ...     print("Configurações OK!")
            ... else:
            ...     print("Verifique as configurações!")
        """
        configuracoes_validas = True
        
        # Verifica a chave da API Groq
        if not cls.GROQ_API_KEY:
            logger.warning(
                "GROQ_API_KEY não configurada. "
                "O OCR de notas fiscais não funcionará. "
                "Configure a variável no arquivo .env"
            )
            configuracoes_validas = False
        
        # Verifica se a SECRET_KEY foi alterada do valor padrão
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            logger.warning(
                "SECRET_KEY usando valor padrão de desenvolvimento. "
                "Configure uma chave segura para produção no arquivo .env"
            )
        
        # Garante que a pasta instance/ existe (para o banco de dados)
        try:
            cls.INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Pasta do banco de dados verificada: {cls.INSTANCE_DIR}")
        except OSError as e:
            logger.error(f"Erro ao criar pasta instance: {e}")
            configuracoes_validas = False
        
        # Garante que a pasta de uploads existe
        try:
            cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            logger.info(f"Pasta de uploads verificada: {cls.UPLOAD_FOLDER}")
        except OSError as e:
            logger.error(f"Erro ao criar pasta de uploads: {e}")
            configuracoes_validas = False
        
        return configuracoes_validas
    
    @classmethod
    def extensao_permitida(cls, filename: str) -> bool:
        """
        Verifica se a extensão do arquivo é permitida para upload.
        
        Args:
            filename: Nome do arquivo a ser verificado
        
        Returns:
            bool: True se a extensão é permitida, False caso contrário
        
        Example:
            >>> Config.extensao_permitida('nota.jpg')
            True
            >>> Config.extensao_permitida('documento.pdf')
            False
        """
        if '.' not in filename:
            return False
        
        extensao = filename.rsplit('.', 1)[1].lower()
        return extensao in cls.ALLOWED_EXTENSIONS
