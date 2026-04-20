from django import forms
from django.contrib.auth import authenticate

from .models import User


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": "Não conseguimos entrar com esses dados. Confira o email e a senha.",
        "inactive": "Seu acesso está temporariamente indisponível. Fale com a clínica para receber ajuda.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages["invalid_login"])
            if not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages["inactive"])
        return cleaned_data

    def get_user(self):
        return self.user_cache


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "wants_in_app_reminders"]
        labels = {
            "full_name": "Nome",
            "wants_in_app_reminders": "Receber lembretes dentro do aplicativo",
        }
