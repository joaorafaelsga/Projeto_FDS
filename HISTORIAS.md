# Histórias de Usuário e Cenários de Validação (BDD)

Este documento apresenta as Histórias de Usuário e os cenários BDD para a plataforma ESGFy, conforme os requisitos da Entrega 03.

---

## [US01] Cadastro e Gestão da Empresa
**Como** gestor de uma pequena ou média empresa,  
**Quero** cadastrar as informações institucionais da minha empresa (nome, setor, porte, e-mail de contato),  
**Para** manter o perfil da organização atualizado na plataforma ESG.

### Cenários de Aceitação (BDD):
* **Cenário 1: Cadastro realizado com sucesso**
  * **Dado que** o gestor está na página de cadastro/edição de empresa,
  * **Quando** preenche todos os campos obrigatórios com dados válidos e clica em "Salvar",
  * **Então** o sistema deve persistir as informações no banco de dados e exibir uma mensagem de confirmação.

* **Cenário 2: Tentativa de envio com campo obrigatório em branco**
  * **Dado que** o gestor está na página de cadastro de empresa,
  * **Quando** deixa o campo "Nome da Empresa" em branco e clica em "Salvar",
  * **Então** o sistema deve impedir o envio e indicar o campo pendente.

---

## [US02] Envio de Mensagens e Suporte (Fale Conosco)
**Como** usuário ou visitante da plataforma,  
**Quero** enviar mensagens de dúvida, sugestões ou suporte através do formulário "Fale Conosco",  
**Para** obter atendimento da equipe técnica e registrar feedbacks.

### Cenários de Aceitação (BDD):
* **Cenário 1: Envio de mensagem com dados válidos**
  * **Dado que** o usuário está na página "Fale Conosco",
  * **Quando** preenche o seu nome, e-mail, assunto e mensagem e clica em "Enviar",
  * **Então** o sistema valida o formulário, grava o comentário no banco de dados e exibe uma mensagem de sucesso.

* **Cenário 2: Tentativa de envio com e-mail inválido**
  * **Dado que** o usuário está na página "Fale Conosco",
  * **Quando** insere um e-mail sem formato válido (ex: `usuario@com`) e submete o formulário,
  * **Então** o sistema invalida a submissão e exige a inserção de um e-mail correto.

---

## [US03] Navegação Institucional e Proposta de Valor
**Como** visitante da plataforma,  
**Quero** acessar as páginas "Quem Somos", "Sobre a Empresa" e "Sobre o Projeto",  
**Para** compreender a metodologia, os objetivos do ESGFy e a equipe responsável.

### Cenários de Aceitação (BDD):
* **Cenário 1: Visualização da página Sobre o Projeto**
  * **Dado que** o visitante navega pelo menu de navegação,
  * **Quando** clica na opção "Sobre o Projeto",
  * **Então** o sistema deve renderizar o template correspondente apresentando o propósito da aplicação e os pilares ESG.

* **Cenário 2: Redirecionamento entre seções institucionais**
  * **Dado que** o visitante está na página inicial,
  * **Quando** clica em "Quem Somos",
  * **Então** o sistema deve carregar os detalhes da equipe de desenvolvimento sem erros de rota.

---
## [US04] Visualização do Diagnóstico por Pilares ESG
**Como** gestor da empresa,  
**Quero** visualizar perguntas e diretrizes divididas pelos pilares Ambiental, Social e Governança,  
**Para** identificar em qual pilar a empresa possui maiores fragilidades e responder de forma organizada.

### Cenários de Aceitação (BDD):
- **Cenário 1: Filtro de perguntas por pilar**
  - **Dado que** o gestor acessou a seção de Diagnóstico,
  - **Quando** seleciona a aba do pilar "Ambiental",
  - **Então** o sistema exibe exclusivamente as perguntas relacionadas às práticas ambientais.

- **Cenário 2: Indicador de progresso por pilar**
  - **Dado que** o gestor está a preencher o questionário,
  - **Quando** responde a algumas perguntas de um pilar,
  - **Então** o sistema deve exibir um indicador de progresso (ex: "3/10 respondidas") para a aba daquele pilar.

---

## [US05] Questionário de Avaliação de Maturidade
**Como** gestor da empresa,  
**Quero** responder a um questionário de avaliação com opções objetivas pontuadas,  
**Para** obter a nota inicial de maturidade sustentável da minha organização.

### Cenários de Aceitação (BDD):
- **Cenário 1: Processamento da nota de maturidade**
  - **Dado que** o gestor respondeu a todas as perguntas do questionário,
  - **Quando** clica em "Submeter Avaliação",
  - **Então** o sistema calcula a pontuação total e exibe o nível de maturidade alcançado (ex: Iniciante, Intermediário, Avançado).

- **Cenário 2: Tentativa de submissão com perguntas em branco**
  - **Dado que** o gestor não respondeu a todas as perguntas obrigatórias,
  - **Quando** tenta clicar em "Submeter Avaliação",
  - **Então** o sistema impede o envio, rola a página para a pergunta pendente e destaca-a com uma mensagem de aviso.

---

## [US06] Emissão de Relatório e Recomendações
**Como** gestor da empresa,  
**Quero** visualizar um relatório final com sugestões de melhoria com base na nota do diagnóstico,  
**Para** elaborar um plano de ação para adequação às práticas ESG.

### Cenários de Aceitação (BDD):
- **Cenário 1: Exibição do plano de ação direcionado**
  - **Dado que** a avaliação da empresa obteve nota baixa no pilar de Governança,
  - **Quando** o relatório final é gerado,
  - **Então** o sistema apresenta recomendações prioritárias voltadas para compliance, ética e transparência corporativa.

- **Cenário 2: Visão geral e comparativa dos pilares**
  - **Dado que** o gestor acessa o relatório final,
  - **Quando** visualiza a página de resultados,
  - **Então** o sistema deve apresentar um gráfico ou tabela comparando a pontuação obtida nos três pilares (E, S, e G).

- **Cenário 3: Impressão ou Exportação do Relatório**
  - **Dado que** o gestor está na tela de relatório final,
  - **Quando** clica na opção "Imprimir / Salvar PDF",
  - **Então** o sistema formata a página de maneira limpa (sem menus de navegação) para facilitar a impressão do plano de ação.
