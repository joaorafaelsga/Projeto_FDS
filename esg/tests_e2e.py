from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from .models import Comentario, Empresa


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