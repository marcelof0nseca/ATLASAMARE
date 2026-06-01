from django.db import migrations, models


def fix_partner_texts(apps, schema_editor):
    Partner = apps.get_model("core", "Partner")

    updates = {
        "Clara Nunes": {
            "description": "Apoio emocional para momentos de ansiedade, espera e tomada de decisão.",
        },
        "Viva Nutrir": {
            "specialty": "Nutrição para fertilidade",
            "description": "Orientação nutricional complementar para rotina alimentar durante o tratamento.",
        },
        "Ponto de Equilibrio": {
            "name": "Ponto de Equilíbrio",
        },
    }

    for current_name, values in updates.items():
        Partner.objects.filter(name=current_name).update(**values)


def reverse_partner_texts(apps, schema_editor):
    Partner = apps.get_model("core", "Partner")

    updates = {
        "Clara Nunes": {
            "description": "Apoio emocional para momentos de ansiedade, espera e tomada de decisao.",
        },
        "Viva Nutrir": {
            "specialty": "Nutricao para fertilidade",
            "description": "Orientacao nutricional complementar para rotina alimentar durante o tratamento.",
        },
        "Ponto de Equilíbrio": {
            "name": "Ponto de Equilibrio",
        },
    }

    for current_name, values in updates.items():
        Partner.objects.filter(name=current_name).update(**values)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_supportcommunity"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partner",
            name="category",
            field=models.CharField(
                choices=[
                    ("psychology", "Psicologia"),
                    ("nutrition", "Nutrição"),
                    ("acupuncture", "Acupuntura"),
                    ("physiotherapy", "Fisioterapia"),
                    ("wellbeing", "Bem-estar"),
                ],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="partner",
            name="tags",
            field=models.CharField(blank=True, help_text="Separe por vírgulas.", max_length=180),
        ),
        migrations.RunPython(fix_partner_texts, reverse_partner_texts),
    ]
