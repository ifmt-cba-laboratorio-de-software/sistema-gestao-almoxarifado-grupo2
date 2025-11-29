from django.db import migrations


def criar_estoques_iniciais(apps, schema_editor):
    Estoque = apps.get_model("estoque", "Estoque")
    nomes = ["Depósito Central", "Sala de manutenção", "Escritório"]
    for nome in nomes:
        Estoque.objects.get_or_create(
            localizacao=nome, defaults={"qtde_atual": 0, "nivel_minimo": 0}
        )


def remover_estoques_iniciais(apps, schema_editor):
    Estoque = apps.get_model("estoque", "Estoque")
    Estoque.objects.filter(localizacao__in=["Depósito Central", "Sala de manutenção", "Escritório"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("estoque", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(criar_estoques_iniciais, remover_estoques_iniciais),
    ]
