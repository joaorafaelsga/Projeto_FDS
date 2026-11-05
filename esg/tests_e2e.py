import base64

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait

from .models import Comentario, Diagnostico, Empresa, Pergunta


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class TestesE2E(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opcoes = webdriver.ChromeOptions()
        # Coloque # na linha abaixo se quiser VER o navegador abrindo
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=opcoes)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    # ---------- funções de ajuda ----------

    def abrir(self, caminho):
        self.driver.get(self.live_server_url + caminho)

    def preencher(self, campo, valor):
        elemento = self.driver.find_element(By.NAME, campo)
        elemento.clear()
        elemento.send_keys(valor)

    def enviar_formulario(self, campo_qualquer):
        self.driver.find_element(By.NAME, campo_qualquer).submit()

    def esperar_texto(self, texto):
        WebDriverWait(self.driver, 5).until(lambda d: texto in d.page_source)

    def pagina_abriu_sem_erro(self):
        html = self.driver.page_source
        self.assertNotIn("Not Found", html)
        self.assertNotIn("Server Error", html)

    # ---------- páginas abrem ----------

    def test_paginas_abrem(self):
        for caminho in ["/", "/quem-somos/", "/empresa/", "/projeto/",
                        "/fale-conosco/", "/cadastrar-empresa/"]:
            with self.subTest(pagina=caminho):
                self.abrir(caminho)
                self.pagina_abriu_sem_erro()

    # ---------- Fale Conosco ----------

    def test_fale_conosco_envia_mensagem(self):
        self.abrir("/fale-conosco/")
        self.preencher("nome", "Lucas Teste")
        self.preencher("email", "lucas@teste.com")
        self.preencher("assunto", "Dúvida sobre ESG")
        self.preencher("mensagem", "Quero saber mais sobre o projeto.")
        self.enviar_formulario("nome")

        self.esperar_texto("Mensagem enviada com sucesso!")
        self.assertEqual(Comentario.objects.count(), 1)
        self.assertEqual(Comentario.objects.first().nome, "Lucas Teste")

    def test_fale_conosco_vazio_nao_salva(self):
        self.abrir("/fale-conosco/")
        self.enviar_formulario("nome")
        self.assertEqual(Comentario.objects.count(), 0)

    def test_fale_conosco_email_invalido_nao_salva(self):
        self.abrir("/fale-conosco/")
        self.preencher("nome", "Lucas Teste")
        self.preencher("email", "email-errado")
        self.preencher("assunto", "Teste")
        self.preencher("mensagem", "Mensagem qualquer")
        self.enviar_formulario("nome")
        self.assertEqual(Comentario.objects.count(), 0)

    # ---------- Cadastrar Empresa ----------

    def test_cadastrar_empresa(self):
        self.abrir("/cadastrar-empresa/")
        self.preencher("nome", "Empresa Verde")
        self.preencher("setor", "Tecnologia")
        self.preencher("porte", "Pequena")
        self.preencher("email_contato", "contato@verde.com")
        self.enviar_formulario("nome")

        WebDriverWait(self.driver, 5).until(lambda d: Empresa.objects.count() == 1)
        self.assertEqual(Empresa.objects.first().nome, "Empresa Verde")

    def test_cadastrar_empresa_vazio_nao_salva(self):
        self.abrir("/cadastrar-empresa/")
        self.enviar_formulario("nome")
        self.assertEqual(Empresa.objects.count(), 0)

    # ---------- Avaliação de maturidade ----------

    def preparar_avaliacao(self):
        empresa = Empresa.objects.create(
            nome="Empresa Sustentável", setor="Serviços", porte="Pequena",
            email_contato="contato@sustentavel.com",
        )
        Pergunta.objects.all().delete()
        perguntas = [
            Pergunta.objects.create(texto=f"Prática {pilar}", pilar=pilar)
            for pilar in Pergunta.Pilar.values
        ]
        self.abrir("/avaliacao/")
        Select(self.driver.find_element(By.NAME, "empresa")).select_by_value(str(empresa.pk))
        return perguntas

    def test_avaliacao_calcula_niveis_no_navegador(self):
        for pontuacao, nivel in [(0, "Iniciante"), (1, "Intermediário"), (2, "Avançado")]:
            with self.subTest(pontuacao=pontuacao):
                perguntas = self.preparar_avaliacao()
                for pergunta in perguntas:
                    self.driver.find_element(
                        By.CSS_SELECTOR,
                        f'input[name="pergunta_{pergunta.pk}"][value="{pontuacao}"]',
                    ).click()
                self.driver.find_element(By.CSS_SELECTOR, ".avaliacao button[type=submit]").click()
                self.esperar_texto("Resultado da Avaliação de Maturidade")
                self.assertIn(nivel, self.driver.page_source)
                diagnostico = Diagnostico.objects.latest("pk")
                self.assertEqual(diagnostico.pontuacao_total, pontuacao * len(perguntas))
                self.assertEqual(diagnostico.respostas.count(), len(perguntas))
                # O próximo caso usa outro conjunto de perguntas.
                Diagnostico.objects.all().delete()

    def test_avaliacao_incompleta_destaca_e_foca_pergunta_pendente(self):
        perguntas = self.preparar_avaliacao()
        for pergunta in perguntas[1:]:
            self.driver.find_element(
                By.CSS_SELECTOR, f'input[name="pergunta_{pergunta.pk}"][value="1"]'
            ).click()
        self.driver.find_element(By.CSS_SELECTOR, ".avaliacao button[type=submit]").click()
        self.esperar_texto("Responda esta pergunta")
        WebDriverWait(self.driver, 5).until(
            lambda driver: driver.switch_to.active_element.get_attribute("name")
            == f"pergunta_{perguntas[0].pk}"
        )
        for pergunta in perguntas[1:]:
            self.assertTrue(self.driver.find_element(
                By.CSS_SELECTOR, f'input[name="pergunta_{pergunta.pk}"][value="1"]'
            ).is_selected())
        self.assertFalse(Diagnostico.objects.exists())


    # ---------- Relatório e recomendações ----------

    def concluir_avaliacao_para_relatorio(self, pontuacoes):
        perguntas = self.preparar_avaliacao()
        for pergunta, pontuacao in zip(perguntas, pontuacoes):
            self.driver.find_element(
                By.CSS_SELECTOR,
                f'input[name="pergunta_{pergunta.pk}"][value="{pontuacao}"]',
            ).click()
        self.driver.find_element(By.CSS_SELECTOR, ".avaliacao button[type=submit]").click()
        WebDriverWait(self.driver, 5).until(
            lambda driver: "Plano de ação recomendado"
            in driver.find_element(By.CSS_SELECTOR, ".relatorio-plano").text
        )

    def test_relatorio_compara_pilares_e_prioriza_governanca(self):
        self.concluir_avaliacao_para_relatorio([2, 2, 0])
        linhas = self.driver.find_elements(By.CSS_SELECTOR, ".relatorio-tabela tbody tr")
        self.assertEqual(len(linhas), 3)
        self.assertIn("Ambiental", linhas[0].text)
        self.assertIn("Governança", linhas[2].text)
        self.assertIn("0 de 2", linhas[2].text)
        primeira_recomendacao = self.driver.find_element(By.CSS_SELECTOR, ".relatorio-recomendacao")
        self.assertIn("Governança", primeira_recomendacao.text)
        self.assertIn("Prioridade: Alta", primeira_recomendacao.text)
        self.assertIn("compliance", primeira_recomendacao.text)

    def test_relatorio_imprime_sem_menu_e_gera_pdf(self):
        self.concluir_avaliacao_para_relatorio([1, 1, 1])
        self.driver.execute_script(
            "window.print = () => { window.impressaoSolicitada = true; };"
        )
        self.driver.find_element(By.ID, "imprimir-relatorio").click()
        self.assertTrue(self.driver.execute_script("return window.impressaoSolicitada;"))

        self.driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": "print"})
        try:
            for seletor in [".navbar", ".site-footer", ".relatorio-acoes"]:
                self.assertFalse(self.driver.find_element(By.CSS_SELECTOR, seletor).is_displayed())
            for seletor in [".relatorio-tabela", ".relatorio-recomendacao"]:
                self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, seletor).is_displayed())
            pdf = self.driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True})
            self.assertTrue(base64.b64decode(pdf["data"]).startswith(b"%PDF-"))
        finally:
            self.driver.execute_cdp_cmd("Emulation.setEmulatedMedia", {"media": ""})
