# Pedido de melhoria

Este é um pedido de melhoria, vou detalha-lo para que possa entender mais precisamente o que preciso.

## Base de conhecimento a seguir

Documentação da API

$HOME/Development/expenselit-api/docs/API/API_DOCUMENTATION.md
$HOME/Development/expenselit-api/docs/API/ExpenseLit API - Complete Documentation.postman_collection.json

Documentação da base de dados

$HOME/Development/expenselit-api/docs/Database/database_documentation.pdf

## Melhoria

Tendo como base as referências acima, preciso que faça o seguinte:

* Percorrer o código e verificar se a lógica de resposta/erro/request está condizente com o que diz a documentação.

* Caso haja campos faltantes ou verificações a serem implementadas, faça.

## Recriação

Depois de implementar, faça o seguinte:

Derrube a aplicação e volumes:

cd $HOME/Development/ExpenseLit/
docker compose down -v
sleep 5

Remova a imagem:

docker image rm expenselit-app:latest
sleep 5

Compile novamente:

docker compose up -d
sleep 5
