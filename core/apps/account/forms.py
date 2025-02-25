from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

class UserRegistrationForm(forms.ModelForm):
    """
    Formulário para registro de novos usuários
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha',
            'autocomplete': 'new-password'
        }),
        label="Senha",
        required=True,
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a Senha',
            'autocomplete': 'new-password'
        }),
        label="Confirme a Senha",
        required=True,
    )

    class Meta:
        model = get_user_model()
        fields = ['full_name', 'email', 'phone_number']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome Completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Whatsapp'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("As senhas não correspondem.")
            if len(password) < 8:
                raise forms.ValidationError("A senha deve ter pelo menos 8 caracteres.")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.phone_number = self.cleaned_data.get('phone_number')  # Adicionando esta linha
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """
    Formulário de login
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'E-mail'
        }),
        label="E-mail",
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha'
        }),
        label="Senha",
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError("Email ou senha inválidos.")
            except User.DoesNotExist:
                raise forms.ValidationError("Email ou senha inválidos.")
        return cleaned_data

class ResetPasswordForm(forms.Form):
    """
    Formulário de recuperação de senha
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'E-mail'
        }),
        label="Entre com seu e-mail",
        required=True
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if not User.objects.filter(email=email).exists():
            # Não informamos ao usuário se o email existe ou não por segurança
            pass
        return email