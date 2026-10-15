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
**Para** identificar em qual pilar a empresa possui maiores fragilidades.

### Cenários de Aceitação (BDD):
* **Cenário 1: Filtro de perguntas por pilar**
  * **Dado que** o gestor acessou a seção de Diagnóstico,
  * **Quando** escolhe o pilar "Ambiental",
  * **Então** o sistema lista apenas os tópicos e perguntas relacionados a práticas ambientais.

---

## [US05] Questionário de Avaliação de Maturidade
**Como** gestor da empresa,  
**Quero** responder a um questionário de avaliação com opções objetivas,  
**Para** obter a nota inicial de maturidade sustentável da minha organização.

### Cenários de Aceitação (BDD):
* **Cenário 1: Processamento da nota de maturidade**
  * **Dado que** o gestor respondeu a todas as perguntas do questionário,
  * **Quando** clica em "Submeter Avaliação",
  * **Então** o sistema calcula a pontuação e exibe o nível de maturidade atingido.

---

## [US06] Emissão de Relatório e Recomendações
**Como** gestor da empresa,  
**Quero** visualizar um relatório final com sugestões de melhoria com base no diagnóstico,  
**Para** elaborar um plano de ação para adequação às normas ESG.

### Cenários de Aceitação (BDD):
* **Cenário 1: Exibição do plano de ação recomendado**
  * **Dado que** a avaliação apontou nota baixa em Governança,
  * **Quando** o relatório final é gerado,
  * **Então** o sistema apresenta recomendações prioritárias de compliance e transparência.
