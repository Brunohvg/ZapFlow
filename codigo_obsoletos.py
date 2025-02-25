import requests
import logging
from decouple import config
from django.http import JsonResponse

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsApp:
    """
    Classe para integração com o serviço de WhatsApp.
    """

    def __init__(self):
        """
        Inicializa a classe WhatsApp com a API_KEY, API_URL e WEBHOOK_URL.
        """
        self.API_KEY = config("WHATSAPP_API_KEY")
        self.API_URL = config("API_URL", default="https://api.lojabibelo.com.br")
        self.WEBHOOK_URL = config("WEBHOOK_URL", default="https://goblin-romantic-imp.ngrok-free.app")

        # Validação das variáveis de ambiente
        for var, name in [(self.API_KEY, "API_KEY"), (self.API_URL, "API_URL"), (self.WEBHOOK_URL, "WEBHOOK_URL")]:
            if not var:
                raise ValueError(f"{name} não configurada")

    def _make_request(self, method, endpoint, data=None):
        """
        Realiza uma requisição HTTP genérica com base no método e endpoint.
        """
        url = f"{self.API_URL}/{endpoint}"
        headers = {
            "accept": "application/json",
            "apikey": self.API_KEY,
            "Content-Type": "application/json",
        }

        try:
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                logger.error(f"Erro 403: Instância já existe para {endpoint}. Detalhes: {response.text}")
                return {"error": "Instância já existe", "status_code": 403}
            logger.error(f"Erro HTTP na solicitação para {endpoint}: {e}")
            return {"error": f"Erro HTTP {response.status_code}", "status_code": response.status_code}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na solicitação para {endpoint}: {e}")
            return {"error": "Falha na conexão"}

    def is_instance_logged_in(self, instance_name):
        """
        Verifica se a instância do WhatsApp está logada.
        """
        response = self._make_request("GET", f"instance/connectionState/{instance_name}")
        return response and response.get("instance", {}).get("state") == "open"

    def create_instance(self, instance_name, number_phone=None):
        """
        Cria uma instância de WhatsApp e retorna o QR Code, token e status.
        """
        data = {
            "instanceName": instance_name,
            "number": number_phone,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True,
        }
        response = self._make_request("POST", "instance/create", data)

        if response and response.get("status_code") == 403:
            logger.warning(f"Instância '{instance_name}' já existe. Pulando criação.")
            return {"error": "Instância já existe", "status_code": 403}

        if response and isinstance(response, dict):
            instance = response.get("instance", {})
            token = response.get("hash")
            pairingCode = response.get("qrcode", {}).get("pairingCode")
            qr_code_data = response.get("qrcode", {}).get("base64")
            status = instance.get("status")

            if instance.get("instanceId") and instance.get("instanceName"):
                self._set_webhook(instance["instanceName"], instance["instanceId"], token)
                return {
                    "status": "success",
                    "qrcode": qr_code_data,
                    "token": token,
                    "instance_id": instance["instanceId"],
                    "status_instance": status,
                    "pairingCode": pairingCode,
                }

        return None, None, None, None, None

    def _set_webhook(self, instance_name, instance_id, token):
        """
        Configura o webhook para a instância criada.
        """
        webhook_data = {
            "webhook": {
                "enabled": True,
                "url": f"{self.WEBHOOK_URL}/zapi/{instance_id}/",
                "headers": {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                "byEvents": False,
                "base64": False,
                "events": ["QRCODE_UPDATED", "CONNECTION_UPDATE"],
            }
        }
        self._make_request("POST", f"webhook/set/{instance_name}", webhook_data)

    def send_message(self, instance_name, number_phone, text):
        """
        Envia uma mensagem de texto para um número especificado.
        """
        data = {
            "number": number_phone,
            "text": text,
            "delay": 1200
        }
        response = self._make_request("POST", f"message/sendText/{instance_name}", data)
        return response if response else {"status_code": 500}

    def _logout_instance(self, instance_name, token):
        """
        Realiza logout da instância.
        """
        return self._perform_instance_action("logout", instance_name, token)

    def _delete_instance(self, instance_name, token):
        """
        Exclui a instância.
        """
        return self._perform_instance_action("delete", instance_name, token)

    def _perform_instance_action(self, action, instance_name, token):
        """
        Realiza ações como logout ou delete para uma instância.
        """
        url = f"{self.API_URL}/instance/{action}/{instance_name}"
        headers = {"apikey": token}

        try:
            response = requests.request("POST" if action == "logout" else "DELETE", url, headers=headers)
            response.raise_for_status()
            logger.info(f"{action.capitalize()} efetuado com sucesso para {instance_name}")
            return JsonResponse({"message": "Success"}, status=200)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao {action} instância {instance_name}: {e}")
            return JsonResponse({"error": f"Falha ao {action} instância"}, status=500)





# Instancia a classe WhatsApp
whatsapp = WhatsApp()

# Define valores de teste
instance_name = "test_instance"
number_phone = "5511999999999"

# Chama a função para criar uma instância e imprime o resultado
result = whatsapp.create_instance(instance_name, number_phone)

print("Resultado do teste:", result)


"""@login_required
def whatsapp(request):
    template_name = 'integration/whatsapp.html'

    if request.method == 'POST':
        name, phone = request.POST.get('id_name'), request.POST.get('id_telefone')

        # Validações iniciais
        if not all([name, phone]):
            messages.error(request, 'Nome e telefone são obrigatórios!')
        elif Integration.objects.filter(tipo='whatsapp', configuracoes_extras__phone=phone).exists() or Integration.objects.filter(nome=name).exists():
            messages.error(request, 'Já existe uma integração com esse telefone!', extra_tags='danger')
        else:
            try:
                whatsapp = WhatsApp()
        
                # Cria a instância e a integração
                instance_name = request.user.email.split('@')[0]
                instance_whatsapp = whatsapp.create_instance(instance_name=instance_name, number_phone=phone)
                
                Integration.objects.create(
                    user=request.user,
                    nome=name,
                    api_key=instance_whatsapp[1],
                    tipo='whatsapp',
                    configuracoes_extras={'phone': phone, 'qr_code': instance_whatsapp[0]}
                )
                
                messages.success(request, 'Integração criada com sucesso!')
                return render(request, template_name)
                    
            except Exception as e:
                messages.error(request, f'Erro ao criar a integração: {str(e)}', extra_tags='danger')

    return render(request, template_name)

"""



"""def whatsapp(request):
    template_name = 'integration/whatsapp.html'
    user = request.user
    integration = Integration.objects.filter(user=user, tipo='whatsapp').first()

    # Garantindo que configuracoes_extras seja sempre um dicionário
    if integration:
        integration.configuracoes_extras = integration.configuracoes_extras or {}

    # Se a integração já está aberta, apenas renderiza a página
    if integration and integration.configuracoes_extras.get('status') == 'open':
        return render(request, template_name, {"integration": integration})

    if request.method == "POST":
        if integration:
            status = integration.configuracoes_extras.get('status')

            if status == 'connecting':
                messages.info(request, 'A conexão com o WhatsApp está em andamento...')
                return render(request, template_name, {"integration": integration})

            elif status in ['expired', 'disconnected']:
                messages.info(request, 'A instância expirou. Gerando um novo QR Code...')
                whatsapp = WhatsApp()
                result = whatsapp.instance_connect(integration.nome, integration.configuracoes_extras.get('number'))

                # Atualizando os dados da integração
                integration.configuracoes_extras.update({
                    "pairingCode": result.get('pairingCode', ''),
                    "qrcode": result.get('qrcode', "")
                })
                integration.save(update_fields=['configuracoes_extras'])
                return render(request, template_name, {"integration": integration})

            else:
                messages.warning(request, f'Você já possui uma instância do WhatsApp ativa: {integration.nome}')
                return render(request, template_name, {"integration": integration})

        else:
            # Criar uma nova integração
            if not user.phone_number:
                messages.error(request, "Seu número de telefone não está cadastrado.", extra_tags='danger')
                return render(request, template_name, {"integration": integration})

            whatsapp = WhatsApp()
            result = whatsapp.create_instance(
                instance_name=user.email.split('@')[0],
                number_phone='55' + str(user.phone_number)
            )

            if not result or result.get("status_code") in [403, 500]:
                messages.error(request, 'Erro ao criar a instância do WhatsApp.', extra_tags='danger')
                return render(request, template_name, {"integration": integration})

            # Criando a integração no banco
            integration = Integration.objects.create(
                user=request.user,
                api_key=result.get('token'),
                nome=result.get('instance_name'),
                tipo='whatsapp',
                configuracoes_extras={
                    "instance_id": result.get('instance_id'),
                    "number": result.get('number'),
                    "status": result.get('status'),
                    "qrcode": result.get('qrcode', {}).get("base64", ""),
                    "pairingCode": result.get('pairingCode', ''),
                }
            )

            messages.success(request, 'Integração criada com sucesso!')

    return render(request, template_name, {"integration": integration})"""




