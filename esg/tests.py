from unittest.mock import patch

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .forms import AvaliacaoForm
from .models import Diagnostico, Empresa, Pergunta, Resposta


class AvaliacaoTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Pergunta.objects.all().delete()
        cls.empresa = Empresa.objects.create(
            nome="Empresa Verde", setor="Tecnologia", porte="Pequena",
            email_contato="contato@verde.com",
        )
        cls.perguntas = [
            Pergunta.objects.create(texto=f"Pr?tica {pilar}", pilar=pilar)
            for pilar in Pergunta.Pilar.values
        ]

    def dados_avaliacao(self, pontuacao=1):
        return {
            "empresa": self.empresa.pk,
            **{f"pergunta_{pergunta.pk}": pontuacao for pergunta in self.perguntas},
        }


class AvaliacaoFormTests(AvaliacaoTestCase):
    def test_aceita_respostas_com_pontuacao_zero(self):
        form = AvaliacaoForm(self.dados_avaliacao(0))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data[f"pergunta_{self.perguntas[0].pk}"], 0)

    def test_indica_pergunta_pendente_sem_descartar_respostas(self):
        dados = self.dados_avaliacao()
        campo = f"pergunta_{self.perguntas[0].pk}"
        del dados[campo]
        form = AvaliacaoForm(dados)
        self.assertFalse(form.is_valid())
        self.assertIn(campo, form.errors)
        self.assertEqual(form[f"pergunta_{self.perguntas[1].pk}"].value(), 1)

    def test_rejeita_empresa_inexistente_e_pontuacao_adulterada(self):
        for alteracao in ({"empresa": 99999}, {f"pergunta_{self.perguntas[0].pk}": 100}):
            with self.subTest(alteracao=alteracao):
                form = AvaliacaoForm({**self.dados_avaliacao(), **alteracao})
                self.assertFalse(form.is_valid())

    def test_impede_avaliacao_sem_perguntas(self):
        Pergunta.objects.all().delete()
        form = AvaliacaoForm({"empresa": self.empresa.pk})
        self.assertFalse(form.is_valid())
        self.assertIn("não possui perguntas", form.non_field_errors()[0])


class PontuacaoDiagnosticoTests(AvaliacaoTestCase):
    def test_calcula_total_e_nivel_nos_limites_das_faixas(self):
        casos = [
            ([0, 0, 0], "iniciante"),
            ([1, 0, 0], "iniciante"),
            ([1, 1, 0], "intermediario"),
            ([1, 1, 1], "intermediario"),
            ([2, 1, 1], "avancado"),
            ([2, 2, 2], "avancado"),
        ]
        for pontuacoes, nivel in casos:
            with self.subTest(pontuacoes=pontuacoes):
                diagnostico = Diagnostico.objects.create(empresa=self.empresa)
                for pergunta, pontuacao in zip(self.perguntas, pontuacoes):
                    Resposta.objects.create(
                        diagnostico=diagnostico, pergunta=pergunta,
                        texto=Resposta.Pontuacao(pontuacao).label,
                        pontuacao=pontuacao,
                    )
                diagnostico.calcular_pontuacao()
                diagnostico.refresh_from_db()
                self.assertEqual(diagnostico.pontuacao_total, sum(pontuacoes))
                self.assertEqual(diagnostico.pontuacao_maxima, 6)
                self.assertEqual(diagnostico.nivel, nivel)

    def test_preserva_resposta_antiga_sem_atribuir_nota_zero(self):
        diagnostico = Diagnostico.objects.create(empresa=self.empresa)
        resposta = Resposta.objects.create(
            diagnostico=diagnostico, pergunta=self.perguntas[0], texto="Resposta antiga"
        )
        self.assertIsNone(resposta.pontuacao)
        with self.assertRaises(ValueError):
            diagnostico.calcular_pontuacao()
        diagnostico.refresh_from_db()
        self.assertIsNone(diagnostico.pontuacao_total)

    def test_nao_calcula_diagnostico_sem_respostas(self):
        diagnostico = Diagnostico.objects.create(empresa=self.empresa)
        with self.assertRaises(ValueError):
            diagnostico.calcular_pontuacao()


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class AvaliacaoViewTests(AvaliacaoTestCase):
    def test_exibe_questionario_agrupado_por_pilar(self):
        response = self.client.get(reverse("avaliacao"))
        self.assertEqual(response.status_code, 200)
        for pergunta in self.perguntas:
            self.assertContains(response, pergunta.texto)
            self.assertContains(response, pergunta.get_pilar_display())
        self.assertContains(response, "Submeter Avaliação")

    def test_salva_respostas_e_exibe_resultado_da_empresa(self):
        response = self.client.post(reverse("avaliacao"), self.dados_avaliacao(), follow=True)
        self.assertRedirects(response, reverse("resultado_avaliacao"))
        diagnostico = Diagnostico.objects.get()
        self.assertEqual(diagnostico.empresa, self.empresa)
        self.assertEqual(diagnostico.respostas.count(), 3)
        self.assertEqual(diagnostico.pontuacao_total, 3)
        self.assertContains(response, "Intermediário")
        self.assertContains(response, "3 de 6 pontos")
        self.assertContains(response, self.empresa.nome)
        for resposta in diagnostico.respostas.all():
            self.assertEqual(resposta.texto, "Em implementação")
        self.client.get(reverse("resultado_avaliacao"))
        self.assertEqual(Diagnostico.objects.count(), 1)

    def test_pergunta_pendente_nao_cria_diagnostico_parcial(self):
        dados = self.dados_avaliacao()
        campo = f"pergunta_{self.perguntas[0].pk}"
        del dados[campo]
        response = self.client.post(reverse("avaliacao"), dados)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "campo-com-erro")
        self.assertContains(response, "Responda esta pergunta")
        self.assertEqual(response.context["form"]["empresa"].value(), str(self.empresa.pk))
        self.assertFalse(Diagnostico.objects.exists())
        self.assertFalse(Resposta.objects.exists())

    def test_recusa_pontuacao_adulterada_sem_salvar(self):
        dados = self.dados_avaliacao()
        dados[f"pergunta_{self.perguntas[0].pk}"] = 100
        response = self.client.post(reverse("avaliacao"), dados)
        self.assertContains(response, "Selecione uma das opções apresentadas.")
        self.assertFalse(Diagnostico.objects.exists())

    def test_resultado_pertence_a_sessao_que_respondeu(self):
        self.client.post(reverse("avaliacao"), self.dados_avaliacao())
        outro_cliente = Client()
        response = outro_cliente.get(reverse("resultado_avaliacao"))
        self.assertRedirects(response, reverse("avaliacao"))

    def test_orienta_cadastro_quando_nao_existem_empresas(self):
        Empresa.objects.all().delete()
        response = self.client.get(reverse("avaliacao"))
        self.assertContains(response, "Cadastre uma empresa")
        self.assertNotContains(response, "Submeter Avaliação")

    def test_questionario_vazio_nao_pode_ser_submetido(self):
        Pergunta.objects.all().delete()
        response = self.client.post(reverse("avaliacao"), {"empresa": self.empresa.pk})
        self.assertContains(response, "não possui perguntas disponíveis")
        self.assertFalse(Diagnostico.objects.exists())

    def test_falha_ao_salvar_respostas_desfaz_criacao_do_diagnostico(self):
        form = AvaliacaoForm(self.dados_avaliacao())
        self.assertTrue(form.is_valid())
        with patch("esg.forms.Resposta.objects.bulk_create", side_effect=RuntimeError):
            with self.assertRaises(RuntimeError):
                form.save()
        self.assertFalse(Diagnostico.objects.exists())
        self.assertFalse(Resposta.objects.exists())


class RelatorioDiagnosticoTests(AvaliacaoTestCase):
    def criar_diagnostico(self, pontuacoes):
        diagnostico = Diagnostico.objects.create(empresa=self.empresa)
        for pergunta, pontuacao in zip(self.perguntas, pontuacoes):
            Resposta.objects.create(
                diagnostico=diagnostico, pergunta=pergunta,
                pontuacao=pontuacao, texto="Resposta da avaliação",
            )
        return diagnostico

    def test_compara_pontuacoes_dos_tres_pilares(self):
        diagnostico = self.criar_diagnostico([2, 1, 0])
        pilares = diagnostico.gerar_relatorio()
        self.assertEqual([pilar["nome"] for pilar in pilares], ["Ambiental", "Social", "Governança"])
        self.assertEqual([pilar["pontuacao"] for pilar in pilares], [2, 1, 0])
        self.assertEqual([pilar["maxima"] for pilar in pilares], [2, 2, 2])
        self.assertEqual([pilar["percentual"] for pilar in pilares], [100, 50, 0])
        self.assertEqual(
            [pilar["prioridade"] for pilar in pilares], ["Acompanhamento", "Média", "Alta"]
        )

    def test_governanca_com_nota_baixa_recebe_acoes_especificas(self):
        diagnostico = self.criar_diagnostico([2, 2, 0])
        governanca = diagnostico.gerar_relatorio()[2]
        orientacoes = " ".join(governanca["recomendacoes"])
        for termo in ["ética", "compliance", "transparentes"]:
            self.assertIn(termo, orientacoes)

    def test_nota_alta_recebe_orientacao_de_acompanhamento(self):
        diagnostico = self.criar_diagnostico([2, 2, 2])
        for pilar in diagnostico.gerar_relatorio():
            self.assertEqual(pilar["prioridade"], "Acompanhamento")
            self.assertIn("Manter as práticas", pilar["recomendacoes"][0])

    def test_nao_confunde_pilar_sem_nota_com_pontuacao_zero(self):
        diagnostico = self.criar_diagnostico([0, None, None])
        ambiental, social, governanca = diagnostico.gerar_relatorio()
        self.assertEqual(ambiental["percentual"], 0)
        self.assertEqual(ambiental["prioridade"], "Alta")
        for pilar in [social, governanca]:
            self.assertIsNone(pilar["percentual"])
            self.assertEqual(pilar["prioridade"], "Sem avaliação")

    def test_pontuacao_maxima_depende_das_respostas_da_avaliacao(self):
        diagnostico = self.criar_diagnostico([2, 1, 0])
        pergunta = Pergunta.objects.create(texto="Outra prática ambiental", pilar="ambiental")
        Resposta.objects.create(
            diagnostico=diagnostico, pergunta=pergunta, pontuacao=0, texto="Não implementada"
        )
        Pergunta.objects.create(texto="Pergunta cadastrada depois", pilar="ambiental")
        ambiental = diagnostico.gerar_relatorio()[0]
        self.assertEqual(ambiental["pontuacao"], 2)
        self.assertEqual(ambiental["maxima"], 4)
        self.assertEqual(ambiental["percentual"], 50)

    def test_relatorio_usa_somente_respostas_do_diagnostico(self):
        primeiro = self.criar_diagnostico([0, 0, 0])
        self.criar_diagnostico([2, 2, 2])
        self.assertEqual([pilar["pontuacao"] for pilar in primeiro.gerar_relatorio()], [0, 0, 0])


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class RelatorioViewTests(AvaliacaoTestCase):
    def enviar_avaliacao(self):
        dados = self.dados_avaliacao(2)
        dados[f"pergunta_{self.perguntas[2].pk}"] = 0
        self.client.post(reverse("avaliacao"), dados)

    def test_resultado_exibe_comparativo_e_governanca_como_prioridade(self):
        self.enviar_avaliacao()
        response = self.client.get(reverse("resultado_avaliacao"))
        self.assertContains(response, "Comparativo dos pilares ESG")
        self.assertContains(response, "Plano de ação recomendado")
        self.assertContains(response, "compliance")
        self.assertEqual(response.context["plano_acao"][0]["nome"], "Governança")
        self.assertEqual(response.context["plano_acao"][0]["prioridade"], "Alta")
        self.assertEqual(len(response.context["pilares"]), 3)

    def test_relatorio_oferece_impressao_e_preserva_nota_salva(self):
        self.enviar_avaliacao()
        response = self.client.get(reverse("resultado_avaliacao"))
        self.assertContains(response, "Imprimir / Salvar PDF")
        self.assertContains(response, "relatorio.js")
        self.assertContains(response, 'class="pagina-relatorio"')
        self.assertContains(response, "4 de 6 pontos")
        self.assertEqual(Diagnostico.objects.count(), 1)

    def test_resultado_sem_avaliacao_redireciona_para_questionario(self):
        self.assertRedirects(
            self.client.get(reverse("resultado_avaliacao")), reverse("avaliacao")
        )
