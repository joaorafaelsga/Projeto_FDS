from django.db import models
from django.db.models import Sum


class Empresa(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome da Empresa")
    setor = models.CharField(max_length=100)
    porte = models.CharField(max_length=50)
    email_contato = models.EmailField(verbose_name="E-mail de Contato", default="contato@empresa.com")
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
    class Nivel(models.TextChoices):
        INICIANTE = "iniciante", "Iniciante"
        INTERMEDIARIO = "intermediario", "Intermediário"
        AVANCADO = "avancado", "Avançado"

    pontuacao_total = models.PositiveIntegerField(null=True, blank=True)
    pontuacao_maxima = models.PositiveIntegerField(null=True, blank=True)
    nivel = models.CharField(max_length=13, choices=Nivel.choices, blank=True)

    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, related_name="diagnosticos"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Diagnóstico {self.pk} - {self.empresa.nome}"

    def calcular_pontuacao(self):
        respostas = self.respostas.all()
        if not respostas.exists() or respostas.filter(pontuacao__isnull=True).exists():
            raise ValueError("Todas as respostas precisam de uma pontuação.")

        self.pontuacao_total = respostas.aggregate(total=Sum("pontuacao"))["total"]
        self.pontuacao_maxima = respostas.count() * max(Resposta.Pontuacao.values)

        if self.pontuacao_total * 3 < self.pontuacao_maxima:
            self.nivel = self.Nivel.INICIANTE
        elif self.pontuacao_total * 3 < self.pontuacao_maxima * 2:
            self.nivel = self.Nivel.INTERMEDIARIO
        else:
            self.nivel = self.Nivel.AVANCADO

        self.save(update_fields=["pontuacao_total", "pontuacao_maxima", "nivel"])


    def gerar_relatorio(self):
        recomendacoes = {
            Pergunta.Pilar.AMBIENTAL: [
                "Medir o consumo de água e energia e definir metas de redução.",
                "Organizar a separação e a destinação correta dos resíduos.",
            ],
            Pergunta.Pilar.SOCIAL: [
                "Revisar as condições de saúde e segurança e orientar a equipe.",
                "Definir ações de diversidade, inclusão e bem-estar dos colaboradores.",
            ],
            Pergunta.Pilar.GOVERNANCA: [
                "Definir um código de ética e conduta e divulgá-lo à equipe.",
                "Revisar o cumprimento das obrigações legais e as práticas de compliance.",
                "Manter registros transparentes das decisões e das finanças da empresa.",
            ],
        }
        notas_por_pilar = {valor: [] for valor in Pergunta.Pilar.values}
        for resposta in self.respostas.select_related("pergunta"):
            if resposta.pontuacao is not None:
                notas_por_pilar[resposta.pergunta.pilar].append(resposta.pontuacao)

        pilares = []
        for valor, nome in Pergunta.Pilar.choices:
            notas = notas_por_pilar[valor]
            total = sum(notas)
            maxima = len(notas) * max(Resposta.Pontuacao.values)
            orientacoes = recomendacoes[valor]

            if not notas:
                prioridade = "Sem avaliação"
                orientacoes = ["Responder às perguntas deste pilar para receber recomendações."]
            elif total * 3 < maxima:
                prioridade = "Alta"
            elif total * 3 < maxima * 2:
                prioridade = "Média"
            else:
                prioridade = "Acompanhamento"
                orientacoes = [
                    f"Manter as práticas de {nome.lower()}, acompanhar seus indicadores "
                    "e revisar os resultados periodicamente."
                ]

            pilares.append({
                "nome": nome,
                "pontuacao": total,
                "maxima": maxima,
                "percentual": total / maxima * 100 if maxima else None,
                "prioridade": prioridade,
                "recomendacoes": orientacoes,
            })
        return pilares


class Resposta(models.Model):
    class Pontuacao(models.IntegerChoices):
        NAO_IMPLEMENTADA = 0, "Não implementada"
        EM_IMPLEMENTACAO = 1, "Em implementação"
        IMPLEMENTADA = 2, "Implementada"

    pontuacao = models.PositiveSmallIntegerField(
        choices=Pontuacao.choices, null=True, blank=True
    )

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