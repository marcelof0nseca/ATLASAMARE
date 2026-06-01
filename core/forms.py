from django import forms

from .models import CommunityPost, PatientTask


class PatientTaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Data",
    )
    due_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time"}),
        label="Hora",
    )

    class Meta:
        model = PatientTask
        fields = ["title", "notes"]
        labels = {
            "title": "Tarefa",
            "notes": "Observação",
        }
        widgets = {
            "notes": forms.TextInput(attrs={"placeholder": "Ex.: separar documentos para a consulta"}),
        }


class CommunityPostForm(forms.ModelForm):
    class Meta:
        model = CommunityPost
        fields = ["category", "body"]
        labels = {
            "category": "Tema",
            "body": "Relato",
        }
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Compartilhe algo que possa acolher outra paciente. Não inclua dados pessoais ou orientações médicas.",
                }
            )
        }
