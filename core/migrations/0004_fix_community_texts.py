from django.db import migrations, models


def fix_community_texts(apps, schema_editor):
    SupportCommunity = apps.get_model("core", "SupportCommunity")

    updates = {
        "Forum anonimo de tentantes": {
            "name": "Fórum anônimo de tentantes",
            "description": "Comunidade BabyCenter Brasil para trocar experiências, dúvidas e acolhimento com outras tentantes.",
            "tags": "fórum,anônimo,tentantes",
        },
        "Rede Fertilidade com Calma": {
            "audience": "Pacientes em tratamento de reprodução assistida",
            "description": "Grupo educativo com encontros online sobre rotina, dúvidas gerais e acolhimento entre pacientes.",
            "tags": "educação,online,acolhimento",
        },
        "Circulo de Espera": {
            "name": "Círculo de Espera",
            "audience": "Pacientes em fases de espera, beta e preparação",
            "description": "Comunidade focada em escuta, ansiedade e pequenas estratégias para atravessar períodos de incerteza.",
        },
        "Relatos reais e acolhimento": {
            "audience": "Tentantes que buscam relatos reais e identificação",
            "description": "Busca pública no Instagram com relatos e vivências compartilhadas por tentantes usando a hashtag #vidadetentante.",
        },
        "Parceiros na Jornada": {
            "description": "Espaço com materiais e conversas para quem acompanha uma paciente durante o tratamento.",
            "support_type": "Conteúdo para rede de apoio",
            "tags": "família,parceiros,rede",
        },
    }

    for current_name, values in updates.items():
        SupportCommunity.objects.filter(name=current_name).update(**values)


def reverse_community_texts(apps, schema_editor):
    SupportCommunity = apps.get_model("core", "SupportCommunity")

    updates = {
        "Fórum anônimo de tentantes": {
            "name": "Forum anonimo de tentantes",
            "description": "Comunidade BabyCenter Brasil para trocar experiencias, duvidas e acolhimento com outras tentantes.",
            "tags": "forum,anonimo,tentantes",
        },
        "Rede Fertilidade com Calma": {
            "audience": "Pacientes em tratamento de reproducao assistida",
            "description": "Grupo educativo com encontros online sobre rotina, duvidas gerais e acolhimento entre pacientes.",
            "tags": "educacao,online,acolhimento",
        },
        "Círculo de Espera": {
            "name": "Circulo de Espera",
            "audience": "Pacientes em fases de espera, beta e preparacao",
            "description": "Comunidade focada em escuta, ansiedade e pequenas estrategias para atravessar periodos de incerteza.",
        },
        "Relatos reais e acolhimento": {
            "audience": "Tentantes que buscam relatos reais e identificacao",
            "description": "Busca publica no Instagram com relatos e vivencias compartilhadas por tentantes usando a hashtag #vidadetentante.",
        },
        "Parceiros na Jornada": {
            "description": "Espaco com materiais e conversas para quem acompanha uma paciente durante o tratamento.",
            "support_type": "Conteudo para rede de apoio",
            "tags": "familia,parceiros,rede",
        },
    }

    for current_name, values in updates.items():
        SupportCommunity.objects.filter(name=current_name).update(**values)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_fix_partner_texts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="supportcommunity",
            name="category",
            field=models.CharField(
                choices=[
                    ("emotional", "Apoio emocional"),
                    ("fertility", "Fertilidade"),
                    ("routine", "Rotina"),
                    ("family", "Família e rede"),
                    ("wellbeing", "Bem-estar"),
                ],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="communitypost",
            name="category",
            field=models.CharField(
                choices=[
                    ("treatment", "Tratamento"),
                    ("routine", "Rotina"),
                    ("feelings", "Acolhimento"),
                    ("hope", "Esperança"),
                ],
                default="feelings",
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name="communityreaction",
            options={"verbose_name": "reação da comunidade", "verbose_name_plural": "reações da comunidade"},
        ),
        migrations.RunPython(fix_community_texts, reverse_community_texts),
    ]
