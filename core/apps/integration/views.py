from django.shortcuts import render, redirect
from .models import Integration
from django.contrib import messages
from core.lib.functions.gerar_token import gerar_token
from .services.whatsapp_service import WhatsApp
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# Create your views here.

def integration(request):
    template_name = 'integration/integracao.html'
    return render(request, template_name)

def whatsapp(request):
    template_name = 'integration/whatsapp.html'
    if request.method == 'POST':
        nome_instancia = request.POST.get('nome_instancia')
        numero_instancia = request.POST.get('numero_instancia')
        token = gerar_token().upper()
        print(token, nome_instancia, numero_instancia)
        response = WhatsApp().create_instance(instance_name=nome_instancia, token=token, number=numero_instancia)

        if 'error' in response:
            messages.error(request, response['error'])
        else:
            messages.success(request, "Instância criada com sucesso!")
            print(response)
    return render(request, template_name)


def nuvemshop(request):
    template_name = 'integration/includes/nuvemshop.html'

    return render(request, template_name)