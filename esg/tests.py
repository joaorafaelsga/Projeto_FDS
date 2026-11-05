from django.test import TestCase

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
