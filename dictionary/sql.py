last_expense_query: str = """
SELECT
    d.descricao AS 'Descrição',
    d.valor AS 'Valor',
    d.data AS 'Data',
    d.categoria AS 'Categoria',
    d.conta AS 'Conta'
FROM
    despesas AS d
INNER JOIN
    contas ON d.conta = contas.nome_conta
    AND d.proprietario_despesa = contas.proprietario_conta
    AND d.documento_proprietario_despesa = contas.documento_proprietario_conta
    INNER JOIN
    usuarios ON d.proprietario_despesa = usuarios.id
    AND d.documento_proprietario_despesa = usuarios.documento
WHERE
    d.categoria NOT IN ('Pix', 'TED', 'DOC', 'Ajuste')
        AND d.descricao NOT IN (
            'Aporte Inicial',
            'Placeholder',
            'Teste'
        )
        AND usuarios.id = %s
        AND usuarios.documento = %s
        AND d.pago = 'S'
ORDER BY d.data DESC, d.id DESC
LIMIT 5;
"""

last_revenue_query: str = """
SELECT
    r.descricao AS 'Descrição',
    r.valor AS Valor,
    r.data AS Data,
    r.categoria AS Categoria,
    r.conta AS Conta
FROM
    receitas AS r
INNER JOIN
    contas ON r.conta = contas.nome_conta
    AND r.proprietario_receita = contas.proprietario_conta
    AND r.documento_proprietario_receita = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON r.proprietario_receita = usuarios.id
        AND r.documento_proprietario_receita = usuarios.documento
WHERE
    r.categoria NOT IN ('Pix' , 'TED', 'DOC', 'Ajuste')
    AND r.data <= %s
        AND usuarios.id = %s
        AND usuarios.documento = %s
        AND r.recebido = 'S'
ORDER BY r.data DESC , r.id DESC
LIMIT 5;
"""

total_expense_query: str = """
SELECT
    CAST(SUM(d.valor) AS DECIMAL (10 , 2 ))
FROM
    despesas AS d
INNER JOIN
    usuarios ON d.proprietario_despesa = usuarios.id
    AND d.documento_proprietario_despesa = usuarios.documento
INNER JOIN
    contas ON d.conta = contas.nome_conta
    AND d.proprietario_despesa = contas.proprietario_conta
    AND d.documento_proprietario_despesa = contas.documento_proprietario_conta
WHERE
    d.pago = 'S'
    AND contas.tipo_conta NOT IN('Fundo de Garantia', 'Vale Alimentação')
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

total_revenue_query: str = """
SELECT
    CAST(SUM(r.valor) AS DECIMAL (10 , 2 ))
FROM
    receitas AS r
INNER JOIN
    usuarios ON r.proprietario_receita = usuarios.id
    AND r.documento_proprietario_receita = usuarios.documento
INNER JOIN
    contas ON r.conta = contas.nome_conta
    AND r.proprietario_receita = contas.proprietario_conta
    AND r.documento_proprietario_receita = contas.documento_proprietario_conta
WHERE
    r.recebido = 'S'
    AND contas.tipo_conta NOT IN ('Fundo de Garantia', 'Vale Alimentação')
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

accounts_revenue_query: str = """
SELECT
    CAST(SUM(r.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    receitas AS r
INNER JOIN
    contas ON r.conta = contas.nome_conta
    AND r.proprietario_receita = contas.proprietario_conta
    AND r.documento_proprietario_receita = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON r.proprietario_receita = usuarios.id
    AND r.documento_proprietario_receita = usuarios.documento
WHERE
    r.data <= %s
        AND r.recebido = 'S'
        AND contas.inativa = 'N'
        AND contas.tipo_conta IN (
            'Conta Corrente',
            'Vale Alimentação',
            'Conta Salário'
        )
        AND usuarios.id = %s
        AND usuarios.documento = %s
GROUP BY conta
ORDER BY conta ASC;
"""

accounts_expenses_query: str = """
SELECT
    CAST(SUM(d.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    despesas AS d
INNER JOIN
    contas ON d.conta = contas.nome_conta
    AND d.proprietario_despesa = contas.proprietario_conta
    AND d.documento_proprietario_despesa = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON d.proprietario_despesa = usuarios.id
    AND d.documento_proprietario_despesa = usuarios.documento
WHERE
    d.data <= %s
    AND d.pago = 'S'
    AND contas.inativa = 'N'
    AND contas.tipo_conta IN (
        'Conta Corrente',
        'Vale Alimentação',
        'Conta Salário'
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY conta
ORDER BY conta ASC;
"""

future_accounts_expenses_query: str = """
SELECT
    CAST(SUM(d.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    despesas AS d
INNER JOIN
    contas ON d.conta = contas.nome_conta
    AND d.proprietario_despesa = contas.proprietario_conta
    AND d.documento_proprietario_despesa = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON d.proprietario_despesa = usuarios.id
    AND d.documento_proprietario_despesa = usuarios.documento
WHERE
    d.data >= %s
    AND d.pago = 'N'
    AND contas.inativa = 'N'
    AND contas.tipo_conta IN (
        'Conta Corrente',
        'Vale Alimentação',
        'Conta Salário'
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY conta
ORDER BY conta ASC;
"""

future_accounts_revenue_query: str = """
SELECT
    CAST(SUM(r.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    receitas AS r
INNER JOIN
    contas ON r.conta = contas.nome_conta
    AND r.proprietario_receita = contas.proprietario_conta
    AND r.documento_proprietario_receita = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON r.proprietario_receita = usuarios.id
    AND r.documento_proprietario_receita = usuarios.documento
WHERE
    r.recebido = 'N'
    AND contas.inativa = 'N'
    AND contas.tipo_conta IN (
        'Conta Corrente',
        'Vale Alimentação',
        'Conta Salário'
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY conta
ORDER BY conta ASC;
"""

accounts_query: str = """
SELECT DISTINCT
    (contas.nome_conta)
FROM
    contas
        INNER JOIN
    usuarios
WHERE
    contas.inativa = 'N'
        AND contas.tipo_conta IN (
            'Conta Corrente',
            'Vale Alimentação',
            'Conta Salário'
        )
        AND contas.proprietario_conta = usuarios.id
        AND contas.documento_proprietario_conta = usuarios.documento
        AND usuarios.id = %s
        AND usuarios.documento = %s
ORDER BY contas.nome_conta;
"""

max_revenue_query: str = """
SELECT
    receitas.descricao AS 'Descrição',
    receitas.valor AS 'Valor',
    receitas.data AS 'Data',
    receitas.categoria AS 'Categoria',
    receitas.conta AS 'Conta'
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        AND receitas.documento_proprietario_receita
        AND contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.id
        AND receitas.documento_proprietario_receita = usuarios.documento
WHERE
    receitas.categoria <> 'Ajuste'
        AND receitas.data <= %s
        AND usuarios.id = %s
        AND usuarios.documento = %s
ORDER BY receitas.valor DESC
LIMIT 5;
"""

max_expense_query: str = """
SELECT
    d.descricao AS 'Descrição',
    d.valor AS 'Valor',
    d.data AS 'Data',
    d.categoria AS 'Categoria',
    d.conta AS 'Conta'
FROM
    despesas AS d
INNER JOIN
    contas ON d.conta = contas.nome_conta
    AND d.proprietario_despesa = contas.proprietario_conta
    AND d.documento_proprietario_despesa = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON d.proprietario_despesa = usuarios.id
        AND d.documento_proprietario_despesa = usuarios.documento
WHERE
    d.categoria <> 'Ajuste'
        AND usuarios.id = %s
        AND usuarios.documento = %s
ORDER BY d.valor DESC
LIMIT 5;
"""

last_expense_id_query: str = """
SELECT id FROM despesas ORDER BY id DESC LIMIT 1;
"""
last_loan_id_query: str = """
SELECT id FROM emprestimos ORDER BY id DESC LIMIT 1;
"""
last_credit_card_expense_id_query: str = """
SELECT id FROM despesas_cartao_credito ORDER BY id DESC LIMIT 1;
"""
last_revenue_id_query: str = """
SELECT id FROM receitas ORDER BY id DESC LIMIT 1;
"""
last_transfer_id_query: str = """
SELECT id FROM transferencias ORDER BY id DESC LIMIT 1;
"""

ticket_revenue_query: str = """
SELECT
    COALESCE(CAST(SUM(r.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    receitas AS r
INNER JOIN
    contas ON r.conta = contas.nome_conta
    AND r.proprietario_receita = contas.proprietario_conta
    AND r.documento_proprietario_receita = contas.documento_proprietario_conta
    INNER JOIN
    usuarios ON r.proprietario_receita = usuarios.id
        AND r.documento_proprietario_receita = usuarios.documento
WHERE
    contas.tipo_conta = 'Vale Alimentação'
    AND contas.inativa = 'N'
    AND r.recebido = 'S'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

ticket_expense_query: str = """
SELECT
    COALESCE(CAST(SUM(d.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    despesas AS d
INNER JOIN
    contas ON d.conta = contas.nome_conta
    AND d.proprietario_despesa = contas.proprietario_conta
    AND d.documento_proprietario_despesa = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON d.proprietario_despesa = usuarios.id
    AND d.documento_proprietario_despesa = usuarios.documento
WHERE
    contas.tipo_conta = 'Vale Alimentação'
    AND contas.inativa = 'N'
    AND d.pago = 'S'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

loan_expense_query: str = """
SELECT
    COALESCE(CAST(SUM(
        emprestimos.valor - emprestimos.valor_pago
    ) AS DECIMAL(10, 2)), 0)
FROM
    emprestimos
INNER JOIN
    usuarios ON emprestimos.credor = usuarios.id
    AND emprestimos.documento_credor = usuarios.documento
WHERE
    emprestimos.pago = 'N'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

debts_expense_query: str = """
SELECT
    COALESCE(CAST(SUM(
        emprestimos.valor - emprestimos.valor_pago
    ) AS DECIMAL (10 , 2 )), 0)
FROM
    emprestimos
        INNER JOIN
    usuarios ON emprestimos.devedor = usuarios.id
    AND emprestimos.documento_devedor = usuarios.documento
WHERE
    emprestimos.pago = 'N'
        AND usuarios.id = %s
        AND usuarios.documento = %s;
"""

fund_revenue_query: str = """
SELECT
    COALESCE(CAST(SUM(r.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    receitas AS r
INNER JOIN
    contas ON r.conta = contas.nome_conta
    AND r.proprietario_receita = contas.proprietario_conta
    AND r.documento_proprietario_receita = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON r.proprietario_receita = usuarios.id
        AND r.documento_proprietario_receita = usuarios.documento
WHERE
    contas.tipo_conta = 'Fundo de Garantia'
    AND r.recebido = 'S'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

fund_expense_query: str = """
SELECT
    COALESCE(CAST(SUM(d.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    despesas AS d
INNER JOIN
    contas ON d.conta = contas.nome_conta
    AND d.proprietario_despesa = contas.proprietario_conta
    AND d.documento_proprietario_despesa = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON d.proprietario_despesa = usuarios.id
    AND d.documento_proprietario_despesa = usuarios.documento
WHERE
    contas.tipo_conta = 'Fundo de Garantia'
        AND d.pago = 'S'
        AND usuarios.id = %s
        AND usuarios.documento = %s;
"""

most_categories_expenses_query: str = """
SELECT
    COALESCE(CAST(SUM(d.valor) AS DECIMAL (10 , 2 )), 0),
    d.categoria
FROM
    despesas AS d
INNER JOIN
    contas ON d.conta = contas.nome_conta
    AND d.proprietario_despesa = contas.proprietario_conta
    AND d.documento_proprietario_despesa = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON d.proprietario_despesa = usuarios.id
        AND d.documento_proprietario_despesa = usuarios.documento
WHERE
    d.categoria NOT IN('Ajuste', 'Fatura Cartão')
    AND contas.tipo_conta IN (
        'Conta Corrente',
        'Vale Alimentação',
        'Conta Salário'
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY d.categoria;"""

most_categories_revenues_query: str = """
SELECT
    COALESCE(CAST(SUM(r.valor) AS DECIMAL (10 , 2 )), 0),
    r.categoria
FROM
    receitas AS r
INNER JOIN
    contas ON r.conta = contas.nome_conta
    AND r.proprietario_receita = contas.proprietario_conta
    AND r.documento_proprietario_receita = contas.documento_proprietario_conta
INNER JOIN
    usuarios ON r.proprietario_receita = usuarios.id
        AND r.documento_proprietario_receita = usuarios.documento
WHERE
    r.categoria <> 'Ajuste'
    AND contas.tipo_conta IN (
        'Conta Corrente',
        'Conta Salário',
        'Vale Alimentação'
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY r.categoria;"""

most_credit_card_expenses_query: str = """
SELECT
    COALESCE(CAST(SUM(dcc.valor) AS DECIMAL (10 , 2 )), 0),
    dcc.categoria
FROM
    despesas_cartao_credito AS dcc
INNER JOIN
    cartao_credito AS cc
    ON dcc.doc_proprietario_cartao = cc.documento_titular
        AND dcc.numero_cartao = cc.numero_cartao
INNER JOIN
    usuarios ON dcc.proprietario_despesa_cartao = usuarios.id
    AND dcc.doc_proprietario_cartao = usuarios.documento
WHERE
    dcc.categoria <> 'Ajuste'
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY dcc.categoria;
"""

owner_cards_query = """
SELECT
    cartao_credito.nome_cartao
FROM
    cartao_credito
        INNER JOIN
    usuarios ON cartao_credito.proprietario_cartao = usuarios.id
        AND cartao_credito.documento_titular = usuarios.documento
WHERE
    usuarios.nome = %s
        AND usuarios.documento = %s;
"""

owner_active_cards_query = """
SELECT
    cartao_credito.nome_cartao
FROM
    cartao_credito
        INNER JOIN
    usuarios ON cartao_credito.proprietario_cartao = usuarios.id
        AND cartao_credito.documento_titular = usuarios.documento
WHERE
    usuarios.nome = %s
        AND usuarios.documento = %s
        AND cartao_credito.inativo = 'N';
"""

user_current_accounts_query = """
SELECT
    contas.nome_conta
FROM
    contas
        INNER JOIN
    usuarios ON contas.proprietario_conta = usuarios.id
        AND contas.documento_proprietario_conta = usuarios.documento
WHERE
    contas.tipo_conta IN (
    'Conta Corrente',
    'Vale Alimentação',
    'Conta Salário'
    )
        AND contas.inativa = 'N'
        AND usuarios.id = %s
        AND usuarios.documento = %s;
"""

user_all_current_accounts_query = """
SELECT
    contas.nome_conta
FROM
    contas
        INNER JOIN
    usuarios ON contas.proprietario_conta = usuarios.id
        AND contas.documento_proprietario_conta = usuarios.documento
WHERE
    contas.tipo_conta IN (
        'Conta Corrente',
        'Vale Alimentação',
        'Conta Salário'
    )
        AND usuarios.id = %s
        AND usuarios.documento = %s;
"""

user_fund_accounts_query = """
SELECT
    contas.nome_conta
FROM
    contas
        INNER JOIN
    usuarios ON contas.proprietario_conta = usuarios.id
        AND contas.documento_proprietario_conta = usuarios.documento
WHERE
    contas.tipo_conta IN ('Fundo de Garantia')
        AND contas.inativa = 'N'
        AND usuarios.id = %s
        AND usuarios.documento = %s;
"""

beneficiaries_query = """
SELECT
    beneficiados.nome
FROM
    beneficiados
        INNER JOIN
    usuarios ON beneficiados.nome <> usuarios.nome
        AND beneficiados.documento <> usuarios.documento
WHERE
    usuarios.nome = %s
        AND usuarios.documento = %s;
"""

creditors_query = """
SELECT
    credores.nome
FROM
    credores
INNER JOIN usuarios ON
    credores.nome <> usuarios.nome
    AND credores.documento <> usuarios.documento
WHERE usuarios.nome = %s AND usuarios.documento = %s;[
]"""

creditor_doc_name_query = """
SELECT
    credores.nome,
    credores.documento
FROM
    credores
        INNER JOIN
    usuarios ON credores.nome = usuarios.id
        AND credores.documento = usuarios.documento
WHERE
    usuarios.nome = %s
    AND usuarios.documento = %s;"""

debtors_query: str = """
SELECT
    emprestimos.devedor
FROM
    emprestimos
INNER JOIN
    beneficiados
    ON emprestimos.devedor = beneficiados.nome
    AND emprestimos.documento_devedor = beneficiados.documento
INNER JOIN
    credores
    ON emprestimos.credor = credores.nome
    AND emprestimos.documento_credor = credores.documento
INNER JOIN
    usuarios
    ON emprestimos.credor = usuarios.id
    AND emprestimos.documento_credor = usuarios.documento
WHERE
    pago = 'N'
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY emprestimos.devedor;
"""

loan_query: str = """
SELECT
    descricao AS 'Descrição',
    valor AS 'Valor Total',
    valor_pago AS 'Valor Pago',
    valor - valor_pago AS 'Valor a Pagar',
    data AS 'Data',
    categoria AS 'Categoria'
FROM
    emprestimos
WHERE
    devedor = %s AND pago = 'N'
ORDER BY data;
"""

total_loan_value_query: str = """
SELECT
    COALESCE(SUM(emprestimos.valor - emprestimos.valor_pago), 0)
FROM
    emprestimos
INNER JOIN
    beneficiados
    ON emprestimos.devedor = beneficiados.nome
    AND emprestimos.documento_devedor = beneficiados.documento
INNER JOIN
    credores ON emprestimos.credor = credores.nome
    AND emprestimos.documento_credor = credores.documento
INNER JOIN
    usuarios ON emprestimos.credor = usuarios.id
    AND emprestimos.documento_credor = usuarios.documento
WHERE
    emprestimos.devedor = %s
    AND usuarios.id = %s
    AND usuarios.documento = %s
        AND pago = 'N';
"""

not_payed_loans_query = """
SELECT
    emprestimos.id AS 'ID',
    emprestimos.descricao AS 'Descrição',
    emprestimos.valor AS 'Valor',
    emprestimos.valor_pago AS 'Valor Pago',
    emprestimos.valor - emprestimos.valor_pago AS 'Valor a Pagar',
    emprestimos.data AS 'Data',
    emprestimos.categoria AS 'Categoria',
    emprestimos.conta AS 'Conta',
    emprestimos.credor AS 'Credor'
FROM
    emprestimos
    INNER JOIN usuarios ON emprestimos.devedor = usuarios.id
    AND emprestimos.documento_devedor = usuarios.documento
WHERE
    usuarios.nome = %s
    AND usuarios.documento = %s
    AND pago = 'N';
"""

not_received_loans_query = """
SELECT
    emprestimos.id AS 'ID',
    emprestimos.descricao AS 'Descrição',
    emprestimos.valor AS 'Valor',
    emprestimos.valor_pago AS 'Valor Pago',
    emprestimos.valor - emprestimos.valor_pago AS 'Valor a Pagar',
    emprestimos.data AS 'Data',
    emprestimos.categoria AS 'Categoria',
    emprestimos.conta AS 'Conta',
    emprestimos.devedor AS 'Devedor'
FROM
    emprestimos
    INNER JOIN usuarios ON emprestimos.credor = usuarios.id
    AND emprestimos.documento_credor = usuarios.documento
WHERE
    usuarios.nome = %s
    AND usuarios.documento = %s
    AND pago = 'N';
"""

not_received_revenue_query = """
SELECT
    r.id,
    r.descricao,
    r.valor,
    r.data,
    r.horario,
    r.categoria,
    r.conta
FROM
    receitas AS r
INNER JOIN
    contas AS c
    ON c.nome_conta = r.conta
    AND c.proprietario_conta = r.proprietario_receita
    AND c.documento_proprietario_conta = r.documento_proprietario_receita
INNER JOIN
    usuarios
    ON r.documento_proprietario_receita = usuarios.documento
    AND r.proprietario_receita = usuarios.id
WHERE
    r.recebido = 'N'
    AND r.data < '2099-12-31'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

not_received_revenue_ids_query = """
SELECT
    r.id
FROM
    receitas AS r
INNER JOIN
    contas ON contas.nome_conta = r.conta
    AND contas.proprietario_conta = r.proprietario_receita
    AND contas.documento_proprietario_conta = r.documento_proprietario_receita
INNER JOIN
    usuarios ON r.documento_proprietario_receita = usuarios.documento
    AND r.proprietario_receita = usuarios.id
WHERE
    r.recebido = 'N'
    AND r.data < '2099-12-31'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

not_payed_expense_query = """
SELECT
    d.id,
    d.descricao,
    d.valor,
    d.data,
    d.horario,
    d.categoria,
    d.conta
FROM
    despesas AS d
INNER JOIN
    contas
    ON contas.nome_conta = d.conta
    AND contas.proprietario_conta = d.proprietario_despesa
    AND contas.documento_proprietario_conta = d.documento_proprietario_despesa
INNER JOIN
    usuarios ON d.documento_proprietario_despesa = usuarios.documento
    AND d.proprietario_despesa = usuarios.id
WHERE
    d.pago = 'N'
    AND d.data < '2099-12-31'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

not_payed_expenses_ids_query = """
SELECT
    d.id
FROM
    despesas AS d
INNER JOIN
    contas ON contas.nome_conta = d.conta
    AND contas.proprietario_conta = d.proprietario_despesa
    AND contas.documento_proprietario_conta = d.documento_proprietario_despesa
INNER JOIN
    usuarios ON d.documento_proprietario_despesa = usuarios.documento
    AND d.proprietario_despesa = usuarios.id
WHERE
    d.pago = 'N'
    AND d.data < '2099-12-31'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

expenses_statement_query = """
SELECT
    despesas.descricao,
    despesas.valor,
    despesas.data,
    despesas.horario,
    despesas.categoria,
    despesas.conta
FROM
    despesas
        INNER JOIN
    contas ON despesas.conta = contas.nome_conta
        AND despesas.proprietario_despesa = contas.proprietario_conta
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.id
        AND despesas.documento_proprietario_despesa = usuarios.documento
WHERE
    despesas.pago = 'S'
        AND despesas.categoria NOT IN('Pix', 'DOC', 'TED', 'Ajuste')
        AND despesas.data >= %s
        AND despesas.data <= %s
        AND despesas.conta IN %s
        AND despesas.valor > 0
        AND usuarios.id = %s
        AND usuarios.documento = %s;
"""

revenues_statement_query = """
SELECT
    receitas.descricao,
    receitas.valor,
    receitas.data,
    receitas.horario,
    receitas.categoria,
    receitas.conta
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.id
        AND receitas.documento_proprietario_receita = usuarios.documento
WHERE
    receitas.recebido = 'S'
        AND receitas.categoria NOT IN('Pix', 'DOC', 'TED')
        AND receitas.data >= %s
        AND receitas.data <= %s
        AND receitas.conta IN %s
        AND usuarios.id = %s
        AND usuarios.documento = %s;
"""

total_account_revenue_query: str = """
SELECT
    CAST(SUM(receitas.valor) AS DECIMAL (10 , 2 ))
FROM
    receitas
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.id
        AND receitas.documento_proprietario_receita = usuarios.documento
WHERE
    receitas.recebido = 'S'
        AND receitas.conta = %s
        AND usuarios.id = %s
        AND usuarios.documento = %s;
"""

total_account_expense_query: str = """
SELECT
    CAST(SUM(despesas.valor) AS DECIMAL (10, 2))
FROM
    despesas
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.id
        AND despesas.documento_proprietario_despesa = usuarios.documento
WHERE
    despesas.pago = 'S'
        AND despesas.conta = %s
        AND usuarios.id = %s
        AND usuarios.documento = %s;
"""

card_invoices_query = """
SELECT
    CONCAT(fc.mes, " de ", fc.ano)
FROM
    fechamentos_cartao AS fc
INNER JOIN
    cartao_credito AS cc
    ON fc.nome_cartao = cc.nome_cartao
    AND fc.numero_cartao = cc.numero_cartao
INNER JOIN
    usuarios
    ON usuarios.documento = fc.documento_titular
WHERE
    fc.nome_cartao = %s
    AND usuarios.id = %s
    AND usuarios.documento = %s
    AND fc.fechado = 'N'
ORDER BY
    fc.data_comeco_fatura;
"""

check_user_query = """SELECT COUNT(id) FROM usuarios;"""

check_if_user_document_exists_query = """
SELECT COUNT(id) FROM usuarios WHERE cpf = %s;
"""
check_if_user_login_exists_query = """
SELECT COUNT(id) FROM usuarios WHERE login = %s;
"""
months_query = """SELECT nome_mes FROM meses;"""

creditors_quantity_query = """
SELECT
    COUNT(id)
FROM
    credores
INNER JOIN
    usuarios
    ON credores.nome = usuarios.id
    AND credores.documento = usuarios.documento
WHERE
    usuarios.login <> %s
    AND usuarios.senha <> %s;
"""
benefited_quantity_query = """
SELECT
    COUNT(id)
FROM
    beneficiados
INNER JOIN
    usuarios
    ON beneficiados.nome <> usuarios.nome
    AND beneficiados.documento <> usuarios.documento
WHERE
    usuarios.nome = %s
    AND usuarios.documento = %s;
"""

account_image_query = """
    SELECT
        contas.caminho_arquivo_imagem
    FROM
        contas
            INNER JOIN
        usuarios ON contas.documento_proprietario_conta = usuarios.documento
            AND contas.proprietario_conta = usuarios.id
    WHERE
        contas.nome_conta = %s
            AND usuarios.id = %s
            AND usuarios.documento = %s;"""

credit_card_expire_date_query = """
SELECT
    cartao_credito.data_validade
FROM
    cartao_credito
WHERE
    cartao_credito.documento_titular = %s
    AND cartao_credito.nome_cartao = %s
    AND cartao_credito.proprietario_cartao = %s;
"""

user_id_query = """SELECT id FROM usuarios WHERE login = %s AND senha = %s;"""
account_id_query = """
SELECT
    contas.id
FROM
    contas
INNER JOIN
    usuarios
    ON usuarios.id = contas.proprietario_conta
WHERE
    id = %s AND senha = %s;
"""
