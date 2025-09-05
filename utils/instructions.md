# Instruções

Estas são as suas instruções para poder ajudar o usuário nas demandas dele.

## Documentação a seguir

`$HOME/Development/expenselit-api/{'app'}.models.py`: Contém a classe das Apps.

`$HOME/Development/expenselit-api/docs/API/ExpenseLit_API_Postman_Collection.json`: Documentação da API.

`$HOME/Development/expenselit-api/docs/Database/database_documentation.md`: Markdown com a estrutura do banco de dados.

`utils/hex.md` : Markdown com a paleta de cores a ser utilizada.

## Ponto principal

O usuário vai lhe reportar através das perguntas o que está ocorrendo:

Erros: Irá te pedir para ler o arquivo utils/errors.md
Melhorias: Irá te pedir para ler o arquivo utils/upgrades.md

## Instruções de escrita de código

Regras inegociaveis:

  Sempre ative o ambiente virtual.
  Siga o padrão de de escrita da convenção PEP8.
  Use o clean code.
  Nomes de funções e classes que deixam claras seus objetivos.
  Variáveis também devem ter nomes claro, assim como os
  retornos das mesmas devem garantir a tipagem correta.
  Documente o código de forma clara.
  Link da documentação: https://peps.python.org/pep-0008/

## Pós processamento do pedido do usuário

  * Analise os erros de tipagem com mypy e Pylance;

  * Com o ambiente virtual ativado e na raiz do projeto, rode o comando:

    flake8 --exclude venv > flake_errors.txt

  * Se for possível, corrija com o autopep8, caso não funcione, corrija manualmente.

  * Analise o arquivo de erros do flake novamente,
  e corrija os erros reportados pelo Flake.

  Refaça o container com o seguinte comando:

    docker compose up --build -d
