## Erro crítico de edição de receita

Ao clicar em uma receita na lista de receitas e clicar em editar, o seguinte erro é mostrado:

❌ Erro ao carregar receitas: st.session_state.edit_revenue_1 cannot be modified after the widget with key edit_revenue_1 is instantiated.

## Erro crítico de edição de despesa

Ao clicar em uma despesa na lista de despesas e clicar em Editar, o seguinte erro é mostrado:

streamlit.errors.StreamlitAPIException: st.session_state.edit_expense_1 cannot be modified after the widget with key edit_expense_1 is instantiated.

Traceback:
File "/app/app.py", line 76, in <module>
    main()
File "/app/app.py", line 69, in main
    HomePage().main_menu()
File "/app/home/main.py", line 103, in main_menu
    page_instance.main_menu(
File "/app/pages/expenses.py", line 90, in main_menu
    self.render()
File "/app/pages/expenses.py", line 107, in render
    self._render_checking_account_expenses()
File "/app/pages/expenses.py", line 122, in _render_checking_account_expenses
    self._render_expenses_list()
File "/app/pages/expenses.py", line 204, in _render_expenses_list
    self._render_expense_card(expense, accounts_map)
File "/app/pages/expenses.py", line 367, in _render_expense_card
    st.session_state[
File "/usr/local/lib/python3.10/dist-packages/streamlit/runtime/metrics_util.py", line 443, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/usr/local/lib/python3.10/dist-packages/streamlit/runtime/state/session_state_proxy.py", line 114, in __setitem__
    get_session_state()[key] = value
File "/usr/local/lib/python3.10/dist-packages/streamlit/runtime/state/safe_session_state.py", line 109, in __setitem__
    self._state[key] = value
File "/usr/local/lib/python3.10/dist-packages/streamlit/runtime/state/session_state.py", line 533, in __setitem__
    raise StreamlitAPIException(

Preciso que corrija definitivamente estes erros.

Crie um módulo de testes interativos com alguma biblioteca que permita automação de cliques, navegações etc.

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


Rode os testes automatizados, e identifique os erros e armazene em error.txt.
