# Instruções

Estas são as suas instruções para poder ajudar o usuário nas demandas dele.

## Documentação a seguir

`$HOME/Development/expenselit-api/{'app'}.models.py` : Contém a classe das Apps.

`$HOME/Development/expenselit-api/docs/API/ExpenseLit API - Complete Documentation.postman_collection.json` : Contém a documentação da API.

`$HOME/Development/expenselit-api/docs/Database/database_documentation.md` : Markdown com a estrutura do banco de dados.

`utils/hex.md` : Markdown com a paleta de cores a ser utilizada.

## Ponto principal

O usuário vai lhe reportar através das perguntas o que está ocorrendo:

Erros: Irá te pedir para ler o arquivo utils/errors.md
Melhorias: Irá te pedir para ler o arquivo utils/upgrades.md

## Instruções de escrita de código

Regras inegociaveis:

  Siga o padrão de de escrita da convenção PEP8.
  Link da documentação: https://peps.python.org/pep-0008/

## Pós processamento do pedido do usuário:

* Depois de implementar a melhoria/erro, faça o seguinte:

  Derrube a aplicação e volumes:

    `cd $HOME/Development/ExpenseLit/`

    `docker compose down -v`

    `sleep 5`

  Remova a imagem:

    `docker image rm expenselit-app:latest`

    `sleep 5`

  Compile novamente:

    `docker compose up -d`

    `sleep 5`
