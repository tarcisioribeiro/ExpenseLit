# Pedido de melhoria

Este é um pedido de melhoria, vou detalha-lo para que possa entender mais precisamente o que preciso.

## Melhoria

---

* Preciso que recrie a tela de transferências.

* A tela de cadastro e listagem devem seguir o mesmo padrão visual, que é o seguinte:

* Duas tabs centralizadas, contendo as opções de listagens de registros do módulo, e outra contendo a opção novo(a) {data módulo}.

### Tela de listagem:

    A listagem deve conter ter os dados legíveis, em 3 st.columns. A primeira com a descrição do registro e emoji das categoria, dados do registro como valor, data ao centro, e a direita, um botão de engrenagem que mostrará um popup com as opções do crud que estejam liberadas para o usuário.

### Tela de registro:
    
    Campos obrigatórios sendo realçados, com valores das listas traduzidos e com emojis nas  categorias
    mantendo os valores de categorias originais.

    Siga os modelos da API para ver como os dados devem ser exibidos de forma legível e como devem ser enviados.

    Use todas as variavéis do arquivo config/settings.py para isso.

### Exemplos

    As telas de contas, despesas e receitas já seguem o padrão que mencionei.

---

## Instruções

    Sempre ative o ambiente virtual.
    Sempre documente em formato NumPy e de forma clara,
    o código que escreveu.
    Se atente a tipagem,
    módulos faltantes e imports não usados,
    usando o MyPy.
    Execute o flake8 para verificar problemas de sintaxe.
    Siga a risca a PEP8, usando o autopep8 quando possível.

## Rebuild

    Refaça o container, com o seguinte comando:

        docker compose up --build -d