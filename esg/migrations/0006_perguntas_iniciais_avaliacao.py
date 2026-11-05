from django.db import migrations


def cadastrar_perguntas(apps, schema_editor):
    Pergunta = apps.get_model("esg", "Pergunta")
    perguntas = [
        ("ambiental", "A empresa adota práticas para reduzir o consumo de água e energia?"),
        ("ambiental", "A empresa separa e destina corretamente os resíduos gerados?"),
        ("social", "A empresa promove a saúde e a segurança dos colaboradores?"),
        ("social", "A empresa adota práticas de diversidade e inclusão?"),
        ("governanca", "A empresa possui orientações de ética e conduta para a equipe?"),
        ("governanca", "A empresa mantém registros transparentes de suas decisões e finanças?"),
    ]
    for pilar, texto in perguntas:
        Pergunta.objects.using(schema_editor.connection.alias).get_or_create(
            pilar=pilar, texto=texto
        )


class Migration(migrations.Migration):
    dependencies = [
        ("esg", "0005_pontuacao_avaliacao"),
    ]

    operations = [
        # As perguntas podem receber respostas; um rollback não deve apagá-las.
        migrations.RunPython(cadastrar_perguntas, migrations.RunPython.noop),
    ]
