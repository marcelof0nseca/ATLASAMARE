from django import forms

from .models import JourneyDocument, JourneyVideo


class JourneyDocumentForm(forms.ModelForm):
    class Meta:
        model = JourneyDocument
        fields = ["treatment", "name", "week", "uploaded_at", "size_label", "file"]
        labels = {
            "treatment": "Tratamento",
            "name": "Nome do arquivo",
            "week": "Semana",
            "uploaded_at": "Data de acesso",
            "size_label": "Tamanho",
            "file": "Arquivo",
        }
        widgets = {
            "week": forms.NumberInput(attrs={"min": 1}),
            "uploaded_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if doctor is not None:
            self.fields["treatment"].queryset = self.fields["treatment"].queryset.filter(
                patient__primary_doctor=doctor,
                is_active=True,
            )
        self.fields["uploaded_at"].input_formats = ["%Y-%m-%dT%H:%M"]


class JourneyVideoForm(forms.ModelForm):
    class Meta:
        model = JourneyVideo
        fields = [
            "title",
            "description",
            "step",
            "duration",
            "video_url",
            "video_file",
            "thumbnail_url",
            "thumbnail_file",
            "is_active",
        ]
        labels = {
            "title": "Titulo",
            "description": "Descricao",
            "step": "Etapa relacionada",
            "duration": "Duracao",
            "video_url": "URL do video",
            "video_file": "Upload do video",
            "thumbnail_url": "URL da thumbnail",
            "thumbnail_file": "Thumbnail",
            "is_active": "Video ativo para pacientes",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "step": forms.NumberInput(attrs={"min": 1}),
        }

    def clean(self):
        cleaned_data = super().clean()
        video_url = cleaned_data.get("video_url")
        video_file = cleaned_data.get("video_file")
        if not video_url and not video_file:
            raise forms.ValidationError("Informe uma URL ou envie um arquivo de video.")
        return cleaned_data
