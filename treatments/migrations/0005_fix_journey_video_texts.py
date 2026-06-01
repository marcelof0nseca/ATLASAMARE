from django.db import migrations


def fix_journey_video_texts(apps, schema_editor):
    JourneyVideo = apps.get_model("treatments", "JourneyVideo")

    updates = {
        "Preparacao para o exame": {
            "title": "Preparação para o exame",
            "description": "Orientações simples para chegar mais tranquila ao exame e saber o que esperar.",
        },
        "Aplicacao da medicacao": {
            "title": "Aplicação da medicação",
            "description": "Passo a passo visual para organizar a rotina antes da aplicação.",
        },
        "Aplicação da medicação": {
            "description": "Passo a passo visual para organizar a rotina antes da aplicação.",
        },
        "Coleta de exames": {
            "description": "Explicação de apoio para entender a coleta e reduzir dúvidas comuns.",
        },
    }

    for current_title, values in updates.items():
        JourneyVideo.objects.filter(title=current_title).update(**values)


def reverse_journey_video_texts(apps, schema_editor):
    JourneyVideo = apps.get_model("treatments", "JourneyVideo")

    updates = {
        "Preparação para o exame": {
            "title": "Preparacao para o exame",
            "description": "Orientacoes simples para chegar mais tranquila ao exame e saber o que esperar.",
        },
        "Aplicação da medicação": {
            "title": "Aplicacao da medicacao",
            "description": "Passo a passo visual para organizar a rotina antes da aplicacao.",
        },
        "Coleta de exames": {
            "description": "Explicacao de apoio para entender a coleta e reduzir duvidas comuns.",
        },
    }

    for current_title, values in updates.items():
        JourneyVideo.objects.filter(title=current_title).update(**values)


class Migration(migrations.Migration):

    dependencies = [
        ("treatments", "0004_journeyvideo"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="journeyvideo",
            options={"ordering": ["step", "title"], "verbose_name": "vídeo da jornada", "verbose_name_plural": "vídeos da jornada"},
        ),
        migrations.RunPython(fix_journey_video_texts, reverse_journey_video_texts),
    ]
