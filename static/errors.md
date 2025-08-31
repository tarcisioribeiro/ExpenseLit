# Log de erro

## Documentação a seguir

`$HOME/Development/expenselit-api/{'app'}.models.py` : Contém a classe das Apps.

`$HOME/Development/expenselit-api/docs/API/ExpenseLit API - Complete Documentation.postman_collection.json` : Contém a documentação da API.

`$HOME/Development/expenselit-api/docs/Database/database_documentation.md` : Markdown com a estrutura do banco de dados.


## Erro(s):

**Obs.**: Vou listar pela ordem de prioridade.

---

1. Erro ao criar fatura quando ainda não há cartão cadastrado
    
    Missing Submit Button

    This form has no submit button, which means that user interactions will never be sent to your Streamlit app.

    To create a submit button, use the st.form_submit_button() function.

    For more information, refer to the documentation for forms.

---

## Instruções

* Faça a varredura do arquivo onde os erros são apresentados.

* Tendo como base a documentação passada anteriormente, encontre uma solução para cada erro e a implemente.

* Depois de implementar, faça o seguinte:

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
