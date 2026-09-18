from django.db import models


class Empresa(models.Model):
    nome = models.CharField(max_length=150)
    setor = models.CharField(max_length=100)
    porte = models.CharField(max_length=50)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
