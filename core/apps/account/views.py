from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password, ValidationError
from datetime import date
from datetime import datetime
from .models import User
from .forms import (UserRegistrationForm, UserLoginForm, ResetPasswordForm,)
from django.core.exceptions import ValidationError



def login_view(request):
    """
    View de login que utiliza email para autenticação
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
        
    form = UserLoginForm(request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            User = get_user_model()
            
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    login(request, user)
                    messages.success(request, "Login realizado com sucesso!")
                    return redirect('dashboard:dashboard')
                else:
                    messages.error(request, "Email ou senha inválidos.", extra_tags='danger')
            except User.DoesNotExist:
                messages.error(request, "Email ou senha inválidos.", extra_tags='danger')
        else:
            for error in form.non_field_errors():
                messages.error(request, error, extra_tags='danger')
    
    return render(request, 'account/login.html', {'form': form})

def register(request):
    """
    View de registro de novos usuários
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
        
    template_name = 'account/register.html'
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Conta criada com sucesso! Faça login para continuar.")
            return redirect('account:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error, extra_tags='danger')
    else:
        form = UserRegistrationForm()
    
    return render(request, template_name, {'form': form})

def reset_password(request):
    """
    View de recuperação de senha
    """
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
        
    template_name = 'account/reset_password.html'
    
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            User = get_user_model()
            
            try:
                user = User.objects.get(email=email)
                # Aqui você implementaria a lógica de envio de email
                # Por exemplo: send_reset_password_email(user)
                messages.success(request, "Se existe uma conta com este e-mail, você receberá instruções para redefinir sua senha.")
            except User.DoesNotExist:
                # Mensagem genérica por segurança
                messages.success(request, "Se existe uma conta com este e-mail, você receberá instruções para redefinir sua senha.")
            return redirect('account:login')
    else:
        form = ResetPasswordForm()

    return render(request, template_name, {'form': form})

@login_required
def profile(request):
    """
    View do perfil do usuário
    """
    template_name = 'account/profile.html'
    return render(request, template_name)

@login_required
def logout_view(request):
    """
    View de logout
    """
    logout(request)
    messages.success(request, "Logout realizado com sucesso!")
    return redirect('account:login')

@login_required
@login_required
def update_profile(request):
    """
    View para atualização de perfil e senha do usuário.
    """
    if request.method == 'POST':
        user = request.user
        update_profile_data = True  # Flag para definir se o perfil será atualizado

        # Atualização de dados do perfil
        user.full_name = request.POST.get('full_name', user.full_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)

        birthdate = request.POST.get('birthdate')
        if birthdate:
            try:
                user.birthdate = date.fromisoformat(birthdate)
            except ValueError:
                messages.error(request, "Formato de data inválido. Use AAAA-MM-DD.", extra_tags='danger')
                update_profile_data = False

        # Captura das senhas
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Se os campos de senha estiverem vazios, permitir salvar os outros dados
        if old_password or new_password1 or new_password2:
            if not all([old_password, new_password1, new_password2]):
                messages.error(request, "Todos os campos de senha são obrigatórios para alteração de senha.", extra_tags='danger')
                update_profile_data = False
            elif user.check_password(old_password):
                if new_password1 == new_password2:
                    try:
                        validate_password(new_password1, user=user)
                        user.set_password(new_password1)
                        messages.success(request, "Senha atualizada com sucesso!")
                    except ValidationError as e:
                        messages.error(request, e.messages[0], extra_tags='danger')
                        update_profile_data = False
                else:
                    messages.error(request, "As novas senhas não correspondem.", extra_tags='danger')
                    update_profile_data = False
            else:
                messages.error(request, "A senha atual está incorreta.", extra_tags='danger')
                update_profile_data = False

        # Salvar alterações do perfil somente se não houver erros
        if update_profile_data:
            user.save()
            messages.success(request, "Dados atualizados com sucesso!")

        return redirect('account:profile')

    return render(request, 'account/profile.html', {'user': request.user})
