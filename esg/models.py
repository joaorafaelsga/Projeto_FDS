from django.db import models


class Empresa(models.Model):
    nome = models.CharField(max_length=150)
    setor = models.CharField(max_length=100)
    porte = models.CharField(max_length=50)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Pergunta(models.Model):
    class Pilar(models.TextChoices):
        AMBIENTAL = "ambiental", "Ambiental"
        SOCIAL = "social", "Social"
        GOVERNANCA = "governanca", "Governança"

    texto = models.CharField(max_length=300)
    pilar = models.CharField(max_length=10, choices=Pilar.choices)

    def __str__(self):
        return self.texto


class Diagnostico(models.Model):
    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="diagnosticos"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnóstico {self.pk} - {self.empresa.nome}"


class Resposta(models.Model):
    diagnostico = models.ForeignKey(
        Diagnostico, on_delete=models.CASCADE, related_name="respostas"
    )
    pergunta = models.ForeignKey(
        Pergunta, on_delete=models.PROTECT, related_name="respostas"
    )
    texto = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["diagnostico", "pergunta"],
                name="resposta_unica_por_pergunta_e_diagnostico",
            )
        ]

    def __str__(self):
        return f"Resposta {self.pk} - {self.pergunta}"

class Comentario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    assunto = models.CharField(max_length=150)
    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.assunto} - {self.nome}"