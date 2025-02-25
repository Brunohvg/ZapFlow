import requests
import logging
from decouple import config

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsApp:
    def __init__(self):
        self.API_KEY = config("WHATSAPP_API_KEY")
        self.API_URL = config("API_URL", default="https://api.lojabibelo.com.br")
        self.WEBHOOK_URL = config("WEBHOOK_URL", default="https://goblin-romantic-imp.ngrok-free.app")

        # Validação das variáveis de ambiente
        if not self.API_KEY:
            raise ValueError("API_KEY não configurada")

    def _make_request(self, method, endpoint, data=None):
        """
            Realiza uma requisição HTTP genérica com base no método e endpoint.
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint da API
            data: Dados a serem enviados na requisição
            status_code: Código de status HTTP da resposta
        """
        url = f"{self.API_URL}/{endpoint}"
        headers = {
            "accept": "application/json",
            "apikey": self.API_KEY,
            "Content-Type": "application/json",
        }

        try:
            # Realiza a requisição
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()  # Levanta uma exceção em caso de erro HTTP
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            # Tratar erros HTTP com status code específico
            return {"error": f"Erro HTTP {e.response.status_code}: {e}", "status_code": e.response.status_code}
        
        except requests.exceptions.RequestException as e:
            # Tratamento de erro de conexão
            return {"error": "Falha na conexão", "status_code": 503}

    def connection_state(self, instance_name):
        """
        Verifica o estado da instância.
        retorna: 'open' (conectado), 'close' (desconectado), 'connecting' (conectando), ou 'Estado desconhecido'.
        Se não encontrar a instância, retorna erro.
        """
        response = self._make_request("GET", f"instance/connectionState/{instance_name}")
        
        # Verifica se houve erro na resposta
        if "error" in response:
            logger.error(f"Erro ao verificar o estado da instância {instance_name}: {response}")
            return None  # Retorna o erro em caso de falha

        # Retorna o estado da instância, se encontrado
        return response.get("instance", {}).get("state", "Estado desconhecido")

    def instance_connect(self, instance_name, number_phone):
       
        """
                Conecta uma instância se ela não estiver aberta.
            Args:
                instance_name (str): O nome da instância a ser conectada.
                number_phone (str): O número de telefone associado à instância.
            Returns:
                dict: Um dicionário contendo o QR code, código de pareamento e contagem, 
                ou uma mensagem de erro se a conexão falhar, ou uma mensagem indicando 
                que a instância já está conectada.

        """
        instance_state = self.connection_state(instance_name=instance_name)

        if instance_state != "open":
            data = {"number": number_phone}
            response = self._make_request(method="GET", endpoint="instance/connect/" + instance_name, data=data)
            
            if not response or "error" in response:
                print("Erro: A resposta da API veio com erro ou está vazia!")
                return {"error": "Falha ao conectar instância", "status_code": 500}

            return {
                "qrcode": response.get("base64", {}),
                "pairingCode": response.get("pairingCode", {}),
                "count": response.get("count", {}),
                }  # Retorna a resposta para quem chamar a função

        return {"message": f"Instância, {instance_name} já está conectada"}

    def create_instance(self, instance_name, number_phone):
        """
        Cria uma instância de WhatsApp e retorna o QR Code, token e status.
        """
        # Verifica se a instância já existe
        instance_state = self.connection_state(instance_name)
        if instance_state is not None:
            logger.error(f"Instância {instance_name} já existe. Estado atual: {instance_state}")
            return {"error": "Instância já existe", "status_code": 403}

        # Dados para criar a instância
        data = {
            "instanceName": instance_name,
            "number": number_phone,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True,
        }

        # Faz a requisição para criar a instância apenas se a instância não existir
        response = self._make_request("POST", "instance/create", data)

        # Verifica se a resposta indica erro (instância já existe)
        if response and response.get("status_code") == 403:
            logger.error(f"Erro 403: Instância já existe para o número {number_phone}. Detalhes: {response}")
            return {"error": "Instância já existe", "status_code": 403}

        # Verifica se os dados esperados estão presentes na resposta
        if response.get("qrcode") and response.get("instance") and response.get("hash"):
            return {
                "instance_id": response.get("instance", {}).get("instanceId"),
                "instance_name": instance_name,
                "number": number_phone,
                "token": response.get("hash"),
                "qrcode": response.get("qrcode"),
                "pairingCode": response.get("qrcode", {}).get("pairingCode"),
                "status": response.get("instance", {}).get("status"),
                "message": "Instância criada com sucesso."
            }
        
        # Se faltarem dados necessários, retorna um erro
        logger.error(f"Erro na criação da instância {instance_name}: Dados incompletos na resposta")
        return {
            "error": "Dados incompletos na resposta da criação da instância",
            "status_code": 500,
        }

    



"""# Exemplo de uso
wp = WhatsApp()
#print(wp.connection_state("Bruno"))
#print(wp.create_instance("12dd", "5511999999999"))
print(wp.instance_connect("Bruno", '55931973121650'))"""
