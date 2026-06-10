from django import forms
from django.contrib.auth import authenticate, update_session_auth_hash

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
        fields = [
            "avatar",
            "full_name",
            "phone",
            "date_of_birth",
            "emergency_contact_name",
            "emergency_contact_phone",
            "wants_in_app_reminders",
            "email_reminders_appointments",
            "email_reminders_journey",
            "email_reminders_maya",
            "reminder_frequency",
        ]
        labels = {
            "avatar": "Foto de perfil",
            "full_name": "Nome",
            "phone": "Telefone",
            "date_of_birth": "Data de nascimento",
            "emergency_contact_name": "Nome do contato",
            "emergency_contact_phone": "Telefone do contato",
            "wants_in_app_reminders": "Lembretes dentro do aplicativo",
            "email_reminders_appointments": "Consultas",
            "email_reminders_journey": "Atualizações da jornada",
            "email_reminders_maya": "Resumos da Maya",
            "reminder_frequency": "Frequência",
        }
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "reminder_frequency": forms.Select(),
        }


class ProfilePushForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["push_notifications_enabled"]
        labels = {"push_notifications_enabled": "Notificações web ativas"}


class ProfileNameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["avatar", "full_name"]
        labels = {"avatar": "Foto de perfil", "full_name": "Nome"}
        widgets = {"avatar": forms.ClearableFileInput()}


class ProfilePersonalForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["phone", "date_of_birth"]
        labels = {"phone": "Telefone", "date_of_birth": "Data de nascimento"}
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}


class ProfileEmergencyForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["emergency_contact_name", "emergency_contact_phone"]
        labels = {
            "emergency_contact_name": "Nome",
            "emergency_contact_phone": "Telefone",
        }


class ProfileNotificationsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "wants_in_app_reminders",
            "email_reminders_appointments",
            "email_reminders_journey",
            "email_reminders_maya",
            "reminder_frequency",
        ]
        labels = {
            "wants_in_app_reminders": "Lembretes dentro do aplicativo",
            "email_reminders_appointments": "Consultas",
            "email_reminders_journey": "Atualizações da jornada",
            "email_reminders_maya": "Resumos da Maya",
            "reminder_frequency": "Frequência",
        }
        widgets = {"reminder_frequency": forms.Select()}


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label="Senha atual",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    new_password = forms.CharField(
        label="Nova senha",
        min_length=8,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    confirm_password = forms.CharField(
        label="Confirmar nova senha",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pwd = self.cleaned_data.get("current_password")
        if not self.user.check_password(pwd):
            raise forms.ValidationError("Senha atual incorreta.")
        return pwd

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password") != cleaned.get("confirm_password"):
            raise forms.ValidationError({"confirm_password": "As senhas não coincidem."})
        return cleaned

    def save(self, request):
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.save()
        update_session_auth_hash(request, self.user)


class DoctorPatientCreateForm(forms.ModelForm):
    initial_password = forms.CharField(
        label="Senha inicial",
        min_length=8,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="A paciente pode trocar a senha depois pelo fluxo da clinica.",
    )

    class Meta:
        model = User
        fields = ["full_name", "email", "wants_in_app_reminders"]
        labels = {
            "full_name": "Nome completo",
            "email": "Email",
            "wants_in_app_reminders": "Receber lembretes dentro do aplicativo",
        }

    def __init__(self, *args, doctor=None, **kwargs):
        self.doctor = doctor
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        patient = super().save(commit=False)
        patient.role = User.Role.PATIENT
        patient.primary_doctor = self.doctor
        patient.set_password(self.cleaned_data["initial_password"])
        if commit:
            patient.save()
        return patient


class DoctorPartnerCreateForm(forms.ModelForm):
    initial_password = forms.CharField(
        label="Senha inicial",
        min_length=8,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="O acompanhante poderá trocar a senha depois pelo próprio perfil.",
    )

    class Meta:
        model = User
        fields = ["full_name", "email", "phone", "wants_in_app_reminders"]
        labels = {
            "full_name": "Nome completo",
            "email": "Email",
            "phone": "Telefone",
            "wants_in_app_reminders": "Receber lembretes dentro do aplicativo",
        }

    def __init__(self, *args, patient=None, **kwargs):
        self.patient = patient
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        partner = super().save(commit=False)
        partner.role = User.Role.PARTNER
        partner.linked_patient = self.patient
        partner.set_password(self.cleaned_data["initial_password"])
        if commit:
            partner.save()
        return partner
