"""
Serviço de integração com Groq para OCR de notas fiscais.

Este módulo fornece a classe GroqService para processar imagens de
notas fiscais e extrair dados estruturados usando o modelo LLaMA Vision.
"""

# 1. Bibliotecas padrão
import base64
import json
import logging
import os
import re
from typing import Optional

# 2. Bibliotecas externas
from groq import Groq

# 3. Imports locais
from config import Config
from utils.helpers import extrair_json_de_texto, validar_data, formatar_valor

# Configuração de logging
logger = logging.getLogger(__name__)


# Prompt do sistema para extração de dados de notas fiscais e comprovantes (DESPESAS)
PROMPT_DESPESA_BASE = """
Você é um assistente contábil especializado em restaurantes/beach clubs.
Analise esta imagem e extraia os dados de despesa.

TIPOS DE DOCUMENTOS ACEITOS:
- Nota fiscal ou cupom fiscal
- Recibo de pagamento
- Comprovante de PIX enviado
- Comprovante de transferência (TED/DOC)
- Boleto pago
- Fatura de serviços (luz, água, internet, telefone)

{nome_arquivo_instrucao}

INSTRUÇÕES:
1. Identifique a data do pagamento/compra (formato: YYYY-MM-DD)
2. Identifique o nome do estabelecimento/fornecedor/beneficiário
3. Extraia o valor TOTAL pago (apenas números, sem R$)
4. Classifique a despesa em CATEGORIA e SUBCATEGORIA conforme abaixo:

CATEGORIAS E SUBCATEGORIAS DISPONÍVEIS:
- Insumos: Frutos do Mar, Carnes e Aves, Hortifruti, Laticínios, Frutas, Alimento (Variado), Gelo, Outros
- Bebidas: Bebidas, Cervejas, Destilados, Vinhos, Energético, Outros
- Operacional: Embalagens, Limpeza, Manutenção, Gás, Organização, Outros
- Pessoal: Pessoal, Pro Labore, Salário, Freelancer, Gorjeta, Venda de Férias, Venda de Folga, Vale Transporte, Vale Refeição, DJ/Músicos, Hora Extra, Outros
- Infraestrutura: Aluguel, Energia, Seguros, Outros
- Administrativo: Impostos, Transporte, Outros
- Marketing e Eventos: Eventos, Marketing, Aluguel, Outros
- Outros: Outros

DICAS PARA CLASSIFICAR:
- Se for pagamento a pessoa física (freelancer, DJ, músico, banda): Pessoal → subcategoria apropriada
- Se for conta de luz/água/energia: Infraestrutura → Energia
- Se for compra de alimentos: Insumos → subcategoria específica
- Se não conseguir identificar claramente: Outros → Outros

RESPONDA APENAS COM JSON VÁLIDO:
{{
    "data": "YYYY-MM-DD",
    "estabelecimento": "Nome do Fornecedor ou Beneficiário",
    "valor_total": 123.45,
    "categoria": "Categoria",
    "subcategoria": "Subcategoria"
}}

Se a imagem não for legível ou não for um documento de despesa, retorne:
{{"erro": "Descrição do problema"}}
"""

# Alias para compatibilidade
PROMPT_DESPESA = PROMPT_DESPESA_BASE.format(nome_arquivo_instrucao="")

# Prompt do sistema para extração de dados de comprovantes de RECEITA (PIX, transferências)
PROMPT_RECEITA = """
Você é um assistente contábil especializado em restaurantes/beach clubs.
Analise esta imagem de comprovante de pagamento e extraia os dados.

INSTRUÇÕES IMPORTANTES:
1. Identifique a data da transação (formato: YYYY-MM-DD)
2. Identifique o nome do pagador ou origem do dinheiro
3. Extraia o valor recebido (apenas números, sem R$)
4. IDENTIFIQUE O TIPO DE PAGAMENTO baseado no conteúdo:
   
   PROCURE ESTAS PALAVRAS-CHAVE:
   - "PIX" ou "Pix" ou "pix" ou "QR Code" ou "chave pix" ou "transferência pix" → tipo_pagamento: "PIX"
   - "Cartão" ou "crédito" ou "débito" ou "visa" ou "mastercard" ou "elo" ou "maquininha" → tipo_pagamento: "Cartão"
   - "TED" ou "DOC" ou "transferência bancária" ou "depósito" → tipo_pagamento: "Transferência"
   - "Cupom fiscal" ou "nota fiscal" ou "venda" ou "recibo" → tipo_pagamento: "Vendas"
   - Se não encontrar nenhuma palavra-chave clara → tipo_pagamento: "Outros"

RESPONDA APENAS COM JSON VÁLIDO:
{
    "data": "YYYY-MM-DD",
    "origem": "Nome do pagador ou banco",
    "valor": 123.45,
    "tipo_pagamento": "PIX"
}

IMPORTANTE: O campo tipo_pagamento DEVE ser exatamente um destes valores:
- "PIX"
- "Cartão"
- "Transferência"
- "Vendas"
- "Outros"

Se a imagem não for legível ou não for um comprovante, retorne:
{"erro": "Descrição do problema"}
"""

# Alias para compatibilidade
PROMPT_SISTEMA = PROMPT_DESPESA


class GroqService:
    """
    Serviço de integração com Groq para OCR de notas fiscais.
    
    Esta classe encapsula toda a lógica de comunicação com a API Groq,
    incluindo preparação de imagens, construção de prompts, chamadas à API
    e validação de respostas.
    
    Attributes:
        client: Cliente Groq para chamadas à API
        model: Nome do modelo de visão a ser utilizado
    
    Example:
        >>> service = GroqService()
        >>> resultado = service.processar_nota(imagem_base64)
        >>> if resultado['sucesso']:
        ...     print(f"Valor: R${resultado['dados']['valor_total']}")
    """
    
    def __init__(self):
        """
        Inicializa cliente Groq com API key do ambiente ou config.
        
        Raises:
            Não levanta exceções, mas loga aviso se API key não estiver configurada.
        """
        self.model = Config.GROQ_MODEL
        self.client = None
        
        # Tenta pegar a API key diretamente do ambiente (prioridade)
        # Isso permite que o WSGI defina a variável antes do config carregar
        api_key = os.environ.get('GROQ_API_KEY') or Config.GROQ_API_KEY
        
        if api_key:
            try:
                # DEBUG FORÇADO PARA LOGS DO SERVIDOR
                masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "CURTA"
                print(f"--- DEBUG GROQ ---")
                print(f"Tentando inicializar com chave: {masked_key}")
                print(f"Tamanho da chave: {len(api_key)}")
                
                self.client = Groq(api_key=api_key)
                logger.info(f"Cliente Groq inicializado com modelo {self.model}")
                print(f"--- SUCESSO GROQ ---")
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente Groq: {e}")
                print(f"--- ERRO GROQ: {str(e)} ---")
        else:
            print("--- ERRO: GROQ_API_KEY VAZIA OU NAO ENCONTRADA ---")
            logger.warning(
                "GROQ_API_KEY não configurada. "
                "O serviço de OCR não funcionará."
            )
    
    def processar_nota(self, imagem_base64: str, nome_arquivo: str = None) -> dict:
        """
        Processa imagem de nota fiscal e extrai dados estruturados.
        
        Args:
            imagem_base64: String base64 da imagem (com ou sem prefixo data:image)
            nome_arquivo: Nome original do arquivo (usado para ajudar na categorização)
        
        Returns:
            dict: Dicionário com resultado do processamento:
                - Se sucesso: {'sucesso': True, 'dados': {...}}
                - Se erro: {'sucesso': False, 'erro': 'mensagem'}
        
        Example:
            >>> with open("nota.jpg", "rb") as f:
            ...     img_b64 = base64.b64encode(f.read()).decode()
            >>> resultado = service.processar_nota(img_b64, "Comprovante_Energia.pdf")
        """
        # Verifica se o cliente está configurado (ou tenta configurar agora)
        if not self.client:
            # Tenta reinicializar (pela força do ódio) caso a ENV tenha carregado depois
            if Config.GROQ_API_KEY:
                try:
                    self.client = Groq(api_key=Config.GROQ_API_KEY)
                    logger.info("Cliente Groq reinicializado com sucesso no momento da chamada")
                except Exception as e:
                    logger.error(f"Erro na reinicialização tardia: {e}")

        if not self.client:
            logger.error("Tentativa de processar nota sem cliente Groq configurado")
            return {
                'sucesso': False,
                'erro': 'Serviço de OCR não configurado. Verifique a GROQ_API_KEY.'
            }
        
        # Valida e prepara a imagem
        imagem_preparada = self._preparar_imagem(imagem_base64)
        if not imagem_preparada:
            return {
                'sucesso': False,
                'erro': 'Imagem inválida. Envie uma imagem em formato válido.'
            }
        
        # Faz a chamada à API
        try:
            logger.info(f"Iniciando processamento de nota fiscal via Groq (arquivo: {nome_arquivo or 'não informado'})")
            
            # Constrói prompt com nome do arquivo se disponível
            prompt = self._construir_prompt(nome_arquivo)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{imagem_preparada}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,  # Baixa para respostas mais determinísticas
                max_tokens=500
            )
            
            texto_resposta = response.choices[0].message.content
            logger.debug(f"Resposta da API Groq: {texto_resposta}")
            
            # Extrai e valida o JSON da resposta
            resultado = self._processar_resposta(texto_resposta)
            
            # ===========================================
            # LÓGICA DE CATEGORIZAÇÃO:
            # 1. Primeiro: Verifica nome do arquivo
            # 2. Segundo: Usa o que a IA identificou do comprovante
            # 3. Fallback: Categoria/Subcategoria = Outros/Outros
            # ===========================================
            if resultado['sucesso'] and nome_arquivo:
                # Tenta categorizar pelo nome do arquivo primeiro
                cat_sub_arquivo = self._categorizar_por_nome_arquivo(nome_arquivo)
                
                if cat_sub_arquivo:
                    # Nome do arquivo tem informação útil - usa ela
                    categoria_arquivo, subcategoria_arquivo = cat_sub_arquivo
                    logger.info(f"Categoria detectada pelo nome do arquivo: {categoria_arquivo}/{subcategoria_arquivo}")
                    resultado['dados']['categoria'] = categoria_arquivo
                    resultado['dados']['subcategoria'] = subcategoria_arquivo
                else:
                    # Nome do arquivo não ajudou - verifica se IA conseguiu identificar
                    categoria_ia = resultado['dados'].get('categoria', 'Outros')
                    subcategoria_ia = resultado['dados'].get('subcategoria', 'Outros')
                    
                    # Se IA não conseguiu identificar (retornou Outros/Outros), mantém assim
                    if categoria_ia == 'Outros' and subcategoria_ia == 'Outros':
                        logger.info("Nenhuma categoria identificada - usando Outros/Outros")
                    else:
                        logger.info(f"Categoria detectada pela IA (comprovante): {categoria_ia}/{subcategoria_ia}")
            
            return resultado
            
        except Exception as e:
            erro_str = str(e)
            logger.error(f"Erro ao chamar API Groq: {erro_str}")
            
            # Erros comuns e mensagens amigáveis
            if 'invalid_api_key' in erro_str.lower() or 'authentication' in erro_str.lower():
                msg_erro = 'Chave da API Groq inválida. Verifique a GROQ_API_KEY no arquivo .env'
            elif 'rate_limit' in erro_str.lower() or 'quota' in erro_str.lower():
                msg_erro = 'Limite de uso da API atingido. Aguarde alguns minutos.'
            elif 'model' in erro_str.lower() and 'not found' in erro_str.lower():
                msg_erro = f'Modelo {self.model} não encontrado. Verifique o GROQ_MODEL no config.'
            elif 'connection' in erro_str.lower() or 'timeout' in erro_str.lower():
                msg_erro = 'Erro de conexão com a API. Verifique sua internet.'
            else:
                msg_erro = f'Erro ao processar: {erro_str[:100]}'
            
            return {
                'sucesso': False,
                'erro': msg_erro
            }
    
    def processar_receita(self, imagem_base64: str) -> dict:
        """
        Processa imagem de comprovante de receita (PIX, transferência) e extrai dados.
        
        Args:
            imagem_base64: String base64 da imagem (com ou sem prefixo data:image)
        
        Returns:
            dict: Dicionário com resultado do processamento:
                - Se sucesso: {'sucesso': True, 'dados': {...}}
                - Se erro: {'sucesso': False, 'erro': 'mensagem'}
        """
        if not self.client:
            logger.error("Tentativa de processar receita sem cliente Groq configurado")
            return {
                'sucesso': False,
                'erro': 'Serviço de OCR não configurado. Verifique a GROQ_API_KEY.'
            }
        
        # Valida e prepara a imagem
        imagem_preparada = self._preparar_imagem(imagem_base64)
        if not imagem_preparada:
            return {
                'sucesso': False,
                'erro': 'Imagem inválida. Envie uma imagem em formato válido.'
            }
        
        try:
            logger.info("Iniciando processamento de comprovante de receita via Groq")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": PROMPT_RECEITA
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{imagem_preparada}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            texto_resposta = response.choices[0].message.content
            logger.debug(f"Resposta da API Groq (receita): {texto_resposta}")
            
            # Processa resposta específica para receita
            return self._processar_resposta_receita(texto_resposta)
            
        except Exception as e:
            erro_str = str(e)
            logger.error(f"Erro ao chamar API Groq (receita): {erro_str}")
            return {
                'sucesso': False,
                'erro': f'Erro ao processar comprovante: {erro_str[:100]}'
            }
    
    def _processar_resposta_receita(self, texto_resposta: str) -> dict:
        """
        Processa e valida a resposta da API Groq para comprovantes de receita.
        """
        dados = extrair_json_de_texto(texto_resposta)
        
        if not dados:
            return {
                'sucesso': False,
                'erro': 'Não foi possível interpretar a resposta da IA.'
            }
        
        if 'erro' in dados:
            return {
                'sucesso': False,
                'erro': dados['erro']
            }
        
        # Normaliza o tipo de pagamento
        tipo_pagamento_raw = dados.get('tipo_pagamento', 'Outros')
        tipo_pagamento = self._normalizar_tipo_pagamento(tipo_pagamento_raw)
        
        # Normaliza os dados de receita
        dados_normalizados = {
            'data': dados.get('data'),
            'origem': dados.get('origem', ''),
            'valor': formatar_valor(dados.get('valor', 0)),
            'tipo_pagamento': tipo_pagamento
        }
        
        logger.info(
            f"Comprovante processado: {dados_normalizados['tipo_pagamento']} - "
            f"R${dados_normalizados['valor']:.2f}"
        )
        
        return {
            'sucesso': True,
            'dados': dados_normalizados
        }
    
    def _normalizar_tipo_pagamento(self, tipo: str) -> str:
        """
        Normaliza o tipo de pagamento para um dos valores válidos.
        """
        if not tipo:
            return 'Outros'
        
        tipo_lower = tipo.lower().strip()
        
        # Mapeamento de variações para tipos válidos
        if 'pix' in tipo_lower:
            return 'PIX'
        elif any(x in tipo_lower for x in ['cartão', 'cartao', 'crédito', 'credito', 'débito', 'debito', 'visa', 'mastercard', 'elo']):
            return 'Cartão'
        elif any(x in tipo_lower for x in ['transferência', 'transferencia', 'ted', 'doc', 'depósito', 'deposito']):
            return 'Transferência'
        elif any(x in tipo_lower for x in ['venda', 'caixa', 'dinheiro', 'cupom', 'nota fiscal']):
            return 'Vendas'
        else:
            return 'Outros'
    
    def _preparar_imagem(self, imagem_base64: str) -> Optional[str]:
        """
        Remove prefixo data:image se existir e valida base64.
        
        Args:
            imagem_base64: String base64 da imagem, possivelmente com prefixo
        
        Returns:
            str: String base64 limpa, ou None se inválida
        """
        if not imagem_base64:
            logger.warning("Imagem base64 vazia recebida")
            return None
        
        try:
            # Remove prefixo data:image/xxx;base64, se existir
            if 'base64,' in imagem_base64:
                imagem_base64 = imagem_base64.split('base64,')[1]
            
            # Remove espaços e quebras de linha
            imagem_base64 = imagem_base64.strip().replace('\n', '').replace('\r', '')
            
            # Valida se é base64 válido tentando decodificar
            decoded = base64.b64decode(imagem_base64)
            
            # Verifica tamanho (máximo ~4MB)
            tamanho_mb = len(decoded) / (1024 * 1024)
            if tamanho_mb > 4:
                logger.warning(f"Imagem muito grande: {tamanho_mb:.2f}MB")
                return None
            
            logger.debug(f"Imagem preparada: {tamanho_mb:.2f}MB")
            return imagem_base64
            
        except Exception as e:
            logger.error(f"Erro ao preparar imagem base64: {e}")
            return None
    
    def _construir_prompt(self, nome_arquivo: str = None) -> str:
        """
        Retorna o prompt do sistema para extração de dados.
        
        Args:
            nome_arquivo: Nome original do arquivo para ajudar na categorização
        
        Returns:
            str: Prompt formatado para a API
        """
        if nome_arquivo:
            # Limpa o nome do arquivo removendo extensão e caracteres especiais
            nome_limpo = nome_arquivo
            if '.' in nome_limpo:
                nome_limpo = nome_limpo.rsplit('.', 1)[0]
            nome_limpo = nome_limpo.replace('_', ' ').replace('-', ' ')
            
            instrucao = f"""IMPORTANTE - NOME DO ARQUIVO: "{nome_limpo}"
O nome do arquivo indica a CATEGORIA da despesa. Use essa informação para classificar corretamente!
Por exemplo: se o nome contém "energia", classifique como "Energia"; se contém "aluguel", classifique como "Aluguel"."""
            
            return PROMPT_DESPESA_BASE.format(nome_arquivo_instrucao=instrucao)
        else:
            return PROMPT_DESPESA
    
    def _processar_resposta(self, texto_resposta: str) -> dict:
        """
        Processa e valida a resposta da API Groq.
        
        Args:
            texto_resposta: Texto retornado pela API
        
        Returns:
            dict: Resultado processado e validado
        """
        # Tenta extrair JSON da resposta
        dados = extrair_json_de_texto(texto_resposta)
        
        if not dados:
            logger.warning(f"Não foi possível extrair JSON da resposta: {texto_resposta}")
            return {
                'sucesso': False,
                'erro': 'Não foi possível interpretar a resposta da IA.'
            }
        
        # Verifica se a IA retornou erro (imagem ilegível, etc.)
        if 'erro' in dados:
            logger.info(f"IA retornou erro: {dados['erro']}")
            return {
                'sucesso': False,
                'erro': dados['erro']
            }
        
        # Valida os campos obrigatórios
        if not self._validar_resposta(dados):
            return {
                'sucesso': False,
                'erro': 'Dados incompletos extraídos da nota. Tente com uma foto mais nítida.'
            }
        
        # Normaliza categoria e subcategoria
        categoria_normalizada = self._normalizar_categoria(dados.get('categoria', 'Outros'))
        subcategoria_raw = dados.get('subcategoria', 'Outros')
        
        # Se subcategoria não foi identificada, usa 'Outros'
        if not subcategoria_raw or subcategoria_raw.strip() == '':
            subcategoria_raw = 'Outros'
        
        # Normaliza os dados
        dados_normalizados = {
            'data': dados.get('data'),
            'estabelecimento': dados.get('estabelecimento', 'Não identificado'),
            'valor_total': formatar_valor(dados.get('valor_total')),
            'categoria': categoria_normalizada,
            'subcategoria': subcategoria_raw
        }
        
        logger.info(
            f"Nota processada com sucesso: {dados_normalizados['estabelecimento']} - "
            f"R${dados_normalizados['valor_total']:.2f} ({categoria_normalizada}/{subcategoria_raw})"
        )
        
        return {
            'sucesso': True,
            'dados': dados_normalizados
        }
    
    def _validar_resposta(self, dados: dict) -> bool:
        """
        Valida se a resposta da IA contém todos os campos obrigatórios.
        Inclui validações anti-alucinação.
        
        Args:
            dados: Dicionário com dados extraídos
        
        Returns:
            bool: True se todos os campos obrigatórios estão presentes e válidos
        """
        if not isinstance(dados, dict):
            logger.warning("Resposta não é um dicionário")
            return False
        
        # Campos obrigatórios
        campos_obrigatorios = ['data', 'valor_total', 'categoria']
        
        for campo in campos_obrigatorios:
            if campo not in dados or dados[campo] is None:
                logger.warning(f"Campo obrigatório ausente: {campo}")
                return False
        
        # ===========================================
        # VALIDAÇÃO ANTI-ALUCINAÇÃO: DATA
        # ===========================================
        data = dados.get('data')
        if data and not validar_data(data):
            logger.warning(f"Data em formato inválido: {data}")
            # Tenta converter alguns formatos comuns
            from utils.helpers import converter_data_para_formato_padrao
            data_convertida = converter_data_para_formato_padrao(data)
            if data_convertida:
                dados['data'] = data_convertida
                logger.info(f"Data convertida para: {data_convertida}")
            else:
                # Se não conseguir converter, usa data de hoje
                from datetime import date
                dados['data'] = date.today().strftime('%Y-%m-%d')
                logger.warning(f"Data inválida, usando data de hoje: {dados['data']}")
        
        # Verifica se a data é razoável (não muito antiga, não futura)
        if data:
            try:
                from datetime import datetime, date as dt_date
                data_parsed = datetime.strptime(dados['data'], '%Y-%m-%d').date()
                hoje = dt_date.today()
                
                # Não aceita datas mais de 2 anos no passado
                anos_atras = (hoje - data_parsed).days / 365
                if anos_atras > 2:
                    logger.warning(f"Data muito antiga detectada (possível alucinação): {data}")
                    dados['data'] = hoje.strftime('%Y-%m-%d')
                
                # Não aceita datas futuras (mais de 1 dia)
                if data_parsed > hoje:
                    dias_futuro = (data_parsed - hoje).days
                    if dias_futuro > 1:
                        logger.warning(f"Data futura detectada (possível alucinação): {data}")
                        dados['data'] = hoje.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        # ===========================================
        # VALIDAÇÃO ANTI-ALUCINAÇÃO: VALOR
        # ===========================================
        valor = dados.get('valor_total')
        try:
            valor_float = formatar_valor(valor)
            
            # Valor zero ou negativo é inválido
            if valor_float <= 0:
                logger.warning(f"Valor total inválido (zero/negativo): {valor}")
                return False
            
            # Valor absurdamente alto pode ser alucinação (> R$ 500.000)
            if valor_float > 500000:
                logger.warning(f"Valor suspeito (muito alto, possível alucinação): R${valor_float}")
                # Não falha, mas loga o aviso - usuário pode corrigir
            
            # Valor muito baixo para nota fiscal (< R$ 0.01)
            if valor_float < 0.01:
                logger.warning(f"Valor suspeito (muito baixo): R${valor_float}")
                return False
                
        except (ValueError, TypeError):
            logger.warning(f"Não foi possível converter valor: {valor}")
            return False
        
        return True
    
    def _categorizar_por_nome_arquivo(self, nome_arquivo: str) -> tuple:
        """
        Tenta determinar a categoria e subcategoria baseado no nome do arquivo.
        Usado como primeira tentativa de categorização.
        
        Args:
            nome_arquivo: Nome original do arquivo
            
        Returns:
            tuple: (categoria, subcategoria) ou None se não conseguir identificar
        """
        if not nome_arquivo:
            return None
        
        nome_lower = nome_arquivo.lower()
        
        # Mapeamento de palavras-chave para (categoria, subcategoria)
        mapeamento = [
            # Pessoal - específicos primeiro (ordem importa!)
            ('dj', 'Pessoal', 'DJ/Músicos'),
            ('musico', 'Pessoal', 'DJ/Músicos'),
            ('banda', 'Pessoal', 'DJ/Músicos'),
            ('som ao vivo', 'Pessoal', 'DJ/Músicos'),
            ('hora extra', 'Pessoal', 'Hora Extra'),
            ('extra', 'Pessoal', 'Hora Extra'),
            ('pro labore', 'Pessoal', 'Pro Labore'),
            ('prolabore', 'Pessoal', 'Pro Labore'),
            ('salario', 'Pessoal', 'Salário'),
            ('salarial', 'Pessoal', 'Salário'),
            ('folha', 'Pessoal', 'Salário'),
            ('beneficio', 'Pessoal', 'Salário'),
            ('vale salarial', 'Pessoal', 'Salário'),
            ('freelancer', 'Pessoal', 'Freelancer'),
            ('pag free', 'Pessoal', 'Freelancer'),
            ('gorjeta', 'Pessoal', 'Gorjeta'),
            ('vt ', 'Pessoal', 'Vale Transporte'),
            ('vale transporte', 'Pessoal', 'Vale Transporte'),
            ('vr ', 'Pessoal', 'Vale Refeição'),
            ('vale refeicao', 'Pessoal', 'Vale Refeição'),
            ('fgts', 'Pessoal', 'Pessoal'),
            ('inss', 'Pessoal', 'Pessoal'),
            ('funcionario', 'Pessoal', 'Pessoal'),
            
            # Infraestrutura
            ('energia', 'Infraestrutura', 'Energia'),
            ('luz', 'Infraestrutura', 'Energia'),
            ('celesc', 'Infraestrutura', 'Energia'),
            ('eletric', 'Infraestrutura', 'Energia'),
            ('agua', 'Infraestrutura', 'Energia'),
            ('casan', 'Infraestrutura', 'Energia'),
            ('aluguel', 'Infraestrutura', 'Aluguel'),
            ('locacao', 'Infraestrutura', 'Aluguel'),
            ('seguro', 'Infraestrutura', 'Seguros'),
            
            # Operacional
            ('gas', 'Operacional', 'Gás'),
            ('botijao', 'Operacional', 'Gás'),
            ('limpeza', 'Operacional', 'Limpeza'),
            ('embalagem', 'Operacional', 'Embalagens'),
            ('descartavel', 'Operacional', 'Embalagens'),
            ('manutencao', 'Operacional', 'Manutenção'),
            ('conserto', 'Operacional', 'Manutenção'),
            ('reparo', 'Operacional', 'Manutenção'),
            ('organizacao', 'Operacional', 'Organização'),
            ('spotify', 'Operacional', 'Música/Streaming'),
            ('deezer', 'Operacional', 'Música/Streaming'),
            ('apple music', 'Operacional', 'Música/Streaming'),
            ('musica ambiente', 'Operacional', 'Música/Streaming'),
            ('streaming', 'Operacional', 'Música/Streaming'),
            ('maquininha', 'Operacional', 'Sistemas/Gestão'),
            ('pagseguro', 'Operacional', 'Sistemas/Gestão'),
            ('stone', 'Operacional', 'Sistemas/Gestão'),
            ('cielo', 'Operacional', 'Sistemas/Gestão'),
            ('getnet', 'Operacional', 'Sistemas/Gestão'),
            ('sumup', 'Operacional', 'Sistemas/Gestão'),
            ('mercado pago', 'Operacional', 'Sistemas/Gestão'),
            ('taxa cartao', 'Operacional', 'Sistemas/Gestão'),
            ('colibri', 'Operacional', 'Sistemas/Gestão'),
            ('pdv', 'Operacional', 'Sistemas/Gestão'),
            ('totvs', 'Operacional', 'Sistemas/Gestão'),
            ('linx', 'Operacional', 'Sistemas/Gestão'),
            
            # Marketing e Eventos
            ('evento', 'Marketing e Eventos', 'Eventos'),
            ('show', 'Marketing e Eventos', 'Eventos'),
            ('festa', 'Marketing e Eventos', 'Eventos'),
            ('facebook', 'Marketing e Eventos', 'Marketing'),
            ('instagram', 'Marketing e Eventos', 'Marketing'),
            ('anuncio', 'Marketing e Eventos', 'Marketing'),
            ('impulsionamento', 'Marketing e Eventos', 'Marketing'),
            ('grafica', 'Marketing e Eventos', 'Marketing'),
            
            # Administrativo
            ('das', 'Administrativo', 'Impostos'),
            ('simples', 'Administrativo', 'Impostos'),
            ('alvara', 'Administrativo', 'Impostos'),
            ('taxa', 'Administrativo', 'Impostos'),
            ('tarifa', 'Administrativo', 'Impostos'),
            ('imposto', 'Administrativo', 'Impostos'),
            ('uber', 'Administrativo', 'Transporte'),
            ('99', 'Administrativo', 'Transporte'),
            ('taxi', 'Administrativo', 'Transporte'),
            ('combustivel', 'Administrativo', 'Transporte'),
            ('gasolina', 'Administrativo', 'Transporte'),
            ('frete', 'Administrativo', 'Transporte'),
            
            # Insumos
            ('camarao', 'Insumos', 'Frutos do Mar'),
            ('peixe', 'Insumos', 'Frutos do Mar'),
            ('frutos do mar', 'Insumos', 'Frutos do Mar'),
            ('carne', 'Insumos', 'Carnes e Aves'),
            ('frango', 'Insumos', 'Carnes e Aves'),
            ('hortifruti', 'Insumos', 'Hortifruti'),
            ('verdura', 'Insumos', 'Hortifruti'),
            ('legume', 'Insumos', 'Hortifruti'),
            ('fruta', 'Insumos', 'Frutas'),
            ('queijo', 'Insumos', 'Laticínios'),
            ('laticinio', 'Insumos', 'Laticínios'),
            ('gelo', 'Insumos', 'Gelo'),
            
            # Bebidas
            ('cerveja', 'Bebidas', 'Cervejas'),
            ('destilado', 'Bebidas', 'Destilados'),
            ('gin', 'Bebidas', 'Destilados'),
            ('vodka', 'Bebidas', 'Destilados'),
            ('whisky', 'Bebidas', 'Destilados'),
            ('vinho', 'Bebidas', 'Vinhos'),
            ('espumante', 'Bebidas', 'Vinhos'),
            ('champagne', 'Bebidas', 'Vinhos'),
            ('energetico', 'Bebidas', 'Energético'),
            ('red bull', 'Bebidas', 'Energético'),
            ('refrigerante', 'Bebidas', 'Refrigerante'),
            ('coca', 'Bebidas', 'Refrigerante'),
            ('guarana', 'Bebidas', 'Refrigerante'),
            ('fanta', 'Bebidas', 'Refrigerante'),
            ('sprite', 'Bebidas', 'Refrigerante'),
            ('pepsi', 'Bebidas', 'Refrigerante'),
            ('bebida', 'Bebidas', 'Bebidas'),
        ]
        
        for chave, categoria, subcategoria in mapeamento:
            if chave in nome_lower:
                logger.info(f"Categoria identificada pelo nome do arquivo: {categoria}/{subcategoria}")
                return (categoria, subcategoria)
        
        return None
    
    def _normalizar_categoria(self, categoria: str) -> str:
        """
        Normaliza categoria para uma das válidas ou retorna 'Outros'.
        
        Args:
            categoria: Categoria retornada pela IA
        
        Returns:
            str: Categoria normalizada (uma das válidas em CATEGORIAS_DESPESA)
        """
        if not categoria:
            return 'Outros'
        
        categoria = categoria.strip()
        
        # Verifica se já é uma categoria válida (case-insensitive)
        for cat_valida in Config.CATEGORIAS_DESPESA:
            if categoria.lower() == cat_valida.lower():
                return cat_valida
        
        # Mapeamento de sinônimos e variações para MONA Beach Club
        mapeamento = {
            # Frutos do Mar
            'camarão': 'Frutos do Mar',
            'camarões': 'Frutos do Mar',
            'peixe': 'Frutos do Mar',
            'peixes': 'Frutos do Mar',
            'salmão': 'Frutos do Mar',
            'polvo': 'Frutos do Mar',
            'ostra': 'Frutos do Mar',
            'ostras': 'Frutos do Mar',
            'lula': 'Frutos do Mar',
            'frutos do mar': 'Frutos do Mar',
            'pescado': 'Frutos do Mar',
            'mariscos': 'Frutos do Mar',
            
            # Carnes e Aves
            'carne': 'Carnes e Aves',
            'carnes': 'Carnes e Aves',
            'frango': 'Carnes e Aves',
            'aves': 'Carnes e Aves',
            'bovina': 'Carnes e Aves',
            'hambúrguer': 'Carnes e Aves',
            'açougue': 'Carnes e Aves',
            'frigorífico': 'Carnes e Aves',
            
            # Hortifruti
            'legumes': 'Hortifruti',
            'verduras': 'Hortifruti',
            'frutas': 'Hortifruti',
            'feira': 'Hortifruti',
            'sacolão': 'Hortifruti',
            'hortifrutigranjeiros': 'Hortifruti',
            
            # Bebidas (não alcoólicas)
            'refrigerante': 'Bebidas',
            'refrigerantes': 'Bebidas',
            'suco': 'Bebidas',
            'sucos': 'Bebidas',
            'água': 'Bebidas',
            'energético': 'Bebidas',
            'café': 'Bebidas',
            
            # Cervejas
            'cerveja': 'Cervejas',
            'cervejas': 'Cervejas',
            'budweiser': 'Cervejas',
            'heineken': 'Cervejas',
            'stella': 'Cervejas',
            'corona': 'Cervejas',
            
            # Destilados
            'gin': 'Destilados',
            'vodka': 'Destilados',
            'whisky': 'Destilados',
            'rum': 'Destilados',
            'tequila': 'Destilados',
            'cachaça': 'Destilados',
            'destilado': 'Destilados',
            
            # Vinhos
            'vinho': 'Vinhos',
            'vinhos': 'Vinhos',
            'champagne': 'Vinhos',
            'espumante': 'Vinhos',
            'champanhe': 'Vinhos',
            
            # Laticínios
            'queijo': 'Laticínios',
            'queijos': 'Laticínios',
            'manteiga': 'Laticínios',
            'leite': 'Laticínios',
            'creme': 'Laticínios',
            'laticínio': 'Laticínios',
            
            # Embalagens
            'embalagem': 'Embalagens',
            'descartáveis': 'Embalagens',
            'guardanapos': 'Embalagens',
            'sacolas': 'Embalagens',
            
            # Limpeza
            'limpeza': 'Limpeza',
            'higiene': 'Limpeza',
            'detergente': 'Limpeza',
            
            # Manutenção
            'manutenção': 'Manutenção',
            'reparo': 'Manutenção',
            'conserto': 'Manutenção',
            'equipamento': 'Manutenção',
            
            # Gás
            'gás': 'Gás',
            'botijão': 'Gás',
            
            # Pessoal
            'salário': 'Pessoal',
            'salarios': 'Pessoal',
            'folha': 'Pessoal',
            'fgts': 'Pessoal',
            'inss': 'Pessoal',
            'funcionário': 'Pessoal',
            'benefício': 'Pessoal',
            'vale': 'Pessoal',
            
            # Aluguel
            'aluguel': 'Aluguel',
            'locação': 'Aluguel',
            'imóvel': 'Aluguel',
            
            # Energia
            'luz': 'Energia',
            'elétrica': 'Energia',
            'celesc': 'Energia',
            'casan': 'Energia',
            'água': 'Energia',
            'energia': 'Energia',
            
            # Seguros
            'seguro': 'Seguros',
            'apólice': 'Seguros',
        }
        
        categoria_lower = categoria.lower()
        for chave, valor in mapeamento.items():
            if chave in categoria_lower:
                logger.debug(f"Categoria '{categoria}' normalizada para '{valor}'")
                return valor
        
        logger.info(f"Categoria '{categoria}' não reconhecida, usando 'Outros'")
        return 'Outros'


# Singleton para reutilização
_groq_service: Optional[GroqService] = None


def get_groq_service() -> GroqService:
    """
    Retorna instância singleton do serviço Groq.
    
    Esta função garante que apenas uma instância do serviço seja criada,
    reutilizando a conexão com a API Groq.
    
    Returns:
        GroqService: Instância singleton do serviço
    
    Example:
        >>> service = get_groq_service()
        >>> resultado = service.processar_nota(imagem)
    """
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service
