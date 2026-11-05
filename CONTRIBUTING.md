# 🤝 Guia de Contribuição — ESGFy

Agradecemos o teu interesse em contribuir para o **ESGFy**! Este documento fornece as diretrizes, convenções e o passo a passo necessário para que qualquer membro da equipa ou colaborador externo possa configurar o ambiente e enviar contribuições para o projeto de forma organizada.

---

## 📋 Índice
- [🛠️ Como Configurar o Ambiente de Desenvolvimento](#️-como-configurar-o-ambiente-de-desenvolvimento)
- [🌿 Fluxo de Trabalho Git e Versionamento](#-fluxo-de-trabalho-git-e-versionamento)
- [📝 Padronização de Commits](#-padronização-de-commits)
- [🔄 Processo de Pull Request (PR)](#-processo-de-pull-request-pr)
- [🧪 Execução de Testes](#-execução-de-testes)
- [🎨 Boas Práticas de Código](#-boas-práticas-de-código)

---

## 🛠️ Como Configurar o Ambiente de Desenvolvimento

Para rodar a aplicação Django localmente na tua máquina, segue o procedimento abaixo:

### 1. Clonar o Repositório
```bash
git clone https://github.com/joaorafaelsga/Projeto_FDS.git
cd Projeto_FDS
```

### 2. Criar e Ativar o Ambiente Virtual (`venv`)
* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 4. Executar as Migrações da Base de Dados
```bash
python manage.py migrate
```

### 5. Iniciar o Servidor de Desenvolvimento
```bash
python manage.py runserver
```
Após o servidor arrancar, acede à aplicação no teu navegador através de: `http://127.0.0.1:8000/`

---

## 🌿 Fluxo de Trabalho Git e Versionamento

Para manter o histórico do repositório limpo e evitar conflitos:

1. **Mantém a branch `main` sempre atualizada:**
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Cria uma branch própria para a tua tarefa:**
   * Para novas funcionalidades: `feature/nome-da-funcionalidade`
   * Para correção de bugs: `fix/descricao-do-bug`
   * Para documentação: `docs/nome-do-documento`
   
   *Exemplo:*
   ```bash
   git checkout -b feature/suporte-fale-conosco
   ```

---

## 📝 Padronização de Commits

Para garantir um versionamento consistente e legível no repositório, adota a seguinte convenção para as mensagens de commit:

* `feat:` Adição de uma nova funcionalidade (ex: `feat: adiciona formulario de contacto na US02`)
* `fix:` Correção de um erro/bug (ex: `fix: corrige validacao de email no formulario`)
* `docs:` Alterações na documentação (ex: `docs: adiciona guia de contribuicao CONTRIBUTING.md`)
* `style:` Formatação, ajuste de CSS/HTML sem alterar lógica (ex: `style: ajusta layout da página sobre`)
* `test:` Adição ou ajuste de testes automatizados (ex: `test: inclui testes Selenium para a US01`)
* `refactor:` Refatoração de código sem alterar funcionalidade externa

> 💡 **Nota sobre frequência de commits:** Realiza commits frequentes para registrar o progresso contínuo do teu trabalho no projeto.

---

## 🔄 Processo de Pull Request (PR)

1. Envia a tua branch para o GitHub:
   ```bash
   git push origin feature/nome-da-funcionalidade
   ```
2. Abre a página do repositório no GitHub e clica em **Compare & pull request**.
3. Escreve um título claro e descreve sucintamente o que foi alterado ou implementado.
4. Aguarda a revisão antes de realizar o *merge* para a branch `main`.

---

## 🧪 Execução de Testes

Antes de submeter o teu Pull Request, verifica se todos os testes unitários e de integração estão a passar:

```bash
python manage.py test
```

Se tiveres implementado testes E2E com o **Selenium**, garante que o navegador e os drivers necessários estão configurados antes de os correr.

---

## 🎨 Boas Práticas de Código

* Segue as recomendações do estilo **PEP 8** para o código Python/Django.
* Mantém as funções e *views* objetivas e com responsabilidade única.
* Nunca envies credenciais, senhas ou chaves secretas no código público (utiliza variáveis de ambiente `.env`).