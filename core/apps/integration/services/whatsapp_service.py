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

        if not self.API_KEY:
            raise ValueError("API_KEY não configurada")

    def _make_request(self, method, endpoint, data=None, params=None):
        """
        Realiza uma requisição HTTP genérica com suporte a `params` na querystring.
        """
        url = f"{self.API_URL}/{endpoint}"
        headers = {
            "accept": "application/json",
            "apikey": self.API_KEY,
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(method, url, headers=headers, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": f"Erro HTTP {e.response.status_code}: {e}", "status_code": e.response.status_code}
        except requests.exceptions.RequestException:
            return {"error": "Falha na conexão", "status_code": 503}

    def create_instance(self, instance_name, token, integration="WHATSAPP-BAILEYS", number=None, qrcode=True):
        """
        Cria uma nova instância no sistema.
        """
        endpoint = "instance/create"
        payload = {
            "instanceName": instance_name,   
            "token": token,
            "integration": integration,
            "qrcode": qrcode,
        }

        # Adiciona o número apenas se for fornecido
        if number:
            payload["number"] = number

        response = self._make_request("POST", endpoint, data=payload)

        if not response or "error" in response:
            logger.error(f"Erro ao criar instância {instance_name}: {response}")
            return {"error": "Falha ao criar instância", "status_code": 500}

        return {
            "instanceName": response.get("instanceName"),
            "instanceId": response.get("instanceId"),
            "status": response.get("status"),
            "apikey": response.get("hash"),
            "qrcode": response.get("qrcode"),
        }

    def instance_connect(self, instance_name, number=None):
        """
        Conecta uma instância específica.
        """
        endpoint = f"instance/connect/{instance_name}"
        params = {"number": number} if number else {}

        response = self._make_request("GET", endpoint, params=params)

        if not response or isinstance(response, dict) and "error" in response:
            logger.error(f"Erro ao conectar a instância {instance_name}: {response}")
            return {"error": "Falha ao conectar instância", "status_code": 500}

        return response

# Exemplo de uso:
wp = WhatsApp()

# Criar uma instância (Número é opcional)
#create_response = wp.create_instance("testss", "MEU_TOKEN",  number="5531973121650")
#print(create_response)

# Conectar uma instância (Número também é opcional)
connect_response = wp.instance_connect("testssss",)
print(connect_response)
