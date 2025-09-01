# Log de erro

Este é um report de erro, vou detalha-lo para que possa entender mais precisamente o que está errado.

## Erro(s):

**Obs.**: Vou listar pela ordem de prioridade.

---

1. Erros ao acessar listagem de transferências:

        NameError: free variable 'category_key' referenced before assignment in enclosing scope
        Traceback:
        File "/app/app.py", line 81, in <module>
            main()
        File "/app/app.py", line 74, in main
            HomePage().main_menu()
        File "/app/home/main.py", line 102, in main_menu
            page_instance.main_menu(
        File "/app/pages/transfers.py", line 53, in main_menu
            self.render()
        File "/app/pages/transfers.py", line 66, in render
            self._render_transfers_list()
        File "/app/pages/transfers.py", line 114, in _render_transfers_list
            filtered_transfers = [
        File "/app/pages/transfers.py", line 117, in <listcomp>
            ) == category_key

2. Erro ao acessar empréstimos:

        UnboundLocalError: local variable 'api_loan_data' referenced before assignment
        Traceback:
        File "/app/app.py", line 81, in <module>
            main()
        File "/app/app.py", line 74, in main
            HomePage().main_menu()
        File "/app/home/main.py", line 102, in main_menu
            page_instance.main_menu(
        File "/app/pages/loans.py", line 53, in main_menu
            self.render()
        File "/app/pages/loans.py", line 68, in render
            self._render_give_loan_form()
        File "/app/pages/loans.py", line 411, in _render_give_loan_form
            self._process_loan_form_submit("given", loan_data)
        File "/app/pages/loans.py", line 585, in _process_loan_form_submit
            api_loan_data['benefited'] = loan_data['benefited_id']

---

## Instruções

* Faça a varredura do arquivo onde os erros são apresentados.

* Tendo como base a documentação passada anteriormente, encontre uma solução para cada erro e a implemente.