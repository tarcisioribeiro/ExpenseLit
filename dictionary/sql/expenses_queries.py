total_account_expense_query: str = """
SELECT
    COALESCE(CAST(SUM(d.valor) AS DECIMAL (10, 2)), 0)
FROM
    despesas AS d
INNER JOIN
    usuarios AS u
    ON d.id_prop_despesa = u.id
    AND d.doc_prop_despesa = u.documento
WHERE
    d.pago = 'S'
    AND d.id_conta = %s
    AND u.id = %s
    AND u.documento = %s;
"""

last_expense_query: str = """
SELECT
    d.descricao AS 'Descrição',
    d.valor AS 'Valor',
    d.data AS 'Data',
    d.categoria AS 'Categoria',
    contas.nome_conta AS 'Conta'
FROM
    despesas AS d
INNER JOIN
    contas ON d.id_conta = contas.id
    AND d.id_prop_despesa = contas.id_prop_conta
    AND d.doc_prop_despesa = contas.doc_prop_conta
    INNER JOIN
    usuarios ON d.id_prop_despesa = usuarios.id
    AND d.doc_prop_despesa = usuarios.documento
WHERE
    d.categoria NOT IN (
        'Ajuste',
        'Pix',
        'DOC',
        'TED'
    )
    AND d.descricao NOT IN (
        'Aporte Inicial',
        'Placeholder',
        'Teste'
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
    AND d.pago = 'S'
ORDER BY
    d.data DESC,
    d.id DESC
LIMIT 5;
"""

total_expense_query: str = """
SELECT
    CAST(SUM(d.valor) AS DECIMAL (10 , 2 ))
FROM
    despesas AS d
INNER JOIN
    usuarios AS u
    ON d.id_prop_despesa = u.id
    AND d.doc_prop_despesa = u.documento
INNER JOIN
    contas AS c
    ON d.id_conta = c.id
    AND d.id_prop_despesa = c.id_prop_conta
    AND d.doc_prop_despesa = c.doc_prop_conta
WHERE
    d.pago = 'S'
    AND c.id_tipo_conta NOT IN(
        'Fundo de Garantia',
        'Vale Alimentação'
    )
    AND u.id = %s
    AND u.documento = %s;
"""

accounts_expenses_query: str = """
SELECT
    CAST(SUM(d.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    despesas AS d
INNER JOIN
    contas AS c
    ON d.id_conta = c.id
    AND d.id_prop_despesa = c.id_prop_conta
    AND d.doc_prop_despesa = c.doc_prop_conta
INNER JOIN
    usuarios ON d.id_prop_despesa = usuarios.id
    AND d.doc_prop_despesa = usuarios.documento
WHERE
    d.data <= %s
    AND d.pago = 'S'
    AND c.inativa = 'N'
    AND c.id_tipo_conta IN (
        SELECT
            id
        FROM
            tipos_conta
        WHERE
            nome IN(
            'Conta Corrente',
            'Vale Alimentação',
            'Conta Salário'
            )
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY c.nome_conta
ORDER BY c.nome_conta ASC;
"""

future_accounts_expenses_query: str = """
SELECT
    CAST(SUM(d.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    despesas AS d
INNER JOIN
    contas AS c
    ON d.id_conta = c.id
    AND d.id_prop_despesa = c.id_prop_conta
    AND d.doc_prop_despesa = c.doc_prop_conta
INNER JOIN
    usuarios ON d.id_prop_despesa = usuarios.id
    AND d.doc_prop_despesa = usuarios.documento
WHERE
    d.data >= %s
    AND d.pago = 'N'
    AND c.inativa = 'N'
    AND c.id_tipo_conta IN (
        SELECT
            id
        FROM
            tipos_conta
        WHERE
            nome IN(
            'Conta Corrente',
            'Vale Alimentação',
            'Conta Salário'
            )
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY c.nome_conta
ORDER BY c.nome_conta ASC;
"""

max_expense_query: str = """
SELECT
    d.descricao AS 'Descrição',
    d.valor AS 'Valor',
    d.data AS 'Data',
    d.categoria AS 'Categoria',
    contas.nome_conta AS 'Conta'
FROM
    despesas AS d
INNER JOIN
    contas ON d.id_conta = contas.id
    AND d.id_prop_despesa = contas.id_prop_conta
    AND d.doc_prop_despesa = contas.doc_prop_conta
INNER JOIN
    usuarios ON d.id_prop_despesa = usuarios.id
        AND d.doc_prop_despesa = usuarios.documento
WHERE
    d.categoria NOT IN (
        'Ajuste',
        'DOC',
        'Pix',
        'TED'
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
ORDER BY
    d.valor DESC
LIMIT 5;
"""

last_expense_id_query: str = """
SELECT id FROM despesas ORDER BY id DESC LIMIT 1;
"""

ticket_expense_query: str = """
SELECT
    COALESCE(CAST(SUM(d.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    despesas AS d
INNER JOIN
    contas ON d.id_conta = contas.id
    AND d.id_prop_despesa = contas.id_prop_conta
    AND d.doc_prop_despesa = contas.doc_prop_conta
INNER JOIN
    usuarios ON d.id_prop_despesa = usuarios.id
    AND d.doc_prop_despesa = usuarios.documento
WHERE
    contas.id_tipo_conta IN (
        SELECT
            id
        FROM
            tipos_conta
        WHERE
            nome = 'Vale Alimentação'
    )
    AND contas.inativa = 'N'
    AND d.pago = 'S'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

fund_expense_query: str = """
SELECT
    COALESCE(CAST(SUM(d.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    despesas AS d
INNER JOIN
    contas ON d.id_conta = contas.id
    AND d.id_prop_despesa = contas.id_prop_conta
    AND d.doc_prop_despesa = contas.doc_prop_conta
INNER JOIN
    usuarios ON d.id_prop_despesa = usuarios.id
    AND d.doc_prop_despesa = usuarios.documento
WHERE
    contas.id_tipo_conta IN(
        SELECT
            id
        FROM
            tipos_conta
        WHERE
            nome = 'Fundo de Garantia'
    )
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
    contas ON d.id_conta = contas.id
    AND d.id_prop_despesa = contas.id_prop_conta
    AND d.doc_prop_despesa = contas.doc_prop_conta
INNER JOIN
    usuarios ON d.id_prop_despesa = usuarios.id
    AND d.doc_prop_despesa = usuarios.documento
WHERE
    d.categoria NOT IN('Ajuste', 'Fatura Cartão')
    AND contas.id_tipo_conta IN (
        SELECT
            id
        FROM
            tipos_conta
        WHERE
            nome IN(
            'Conta Corrente',
            'Conta Salário'
            )
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY d.categoria;
"""

not_payed_expense_query = """
SELECT
    d.id,
    d.descricao,
    d.valor,
    d.data,
    d.horario,
    d.categoria,
    c.nome_conta
FROM
    despesas AS d
INNER JOIN
    contas AS c
    ON c.id_prop_conta = d.id_prop_despesa
    AND c.doc_prop_conta = d.doc_prop_despesa
    AND c.id = d.id_conta
INNER JOIN
    usuarios AS u
    ON d.doc_prop_despesa = u.documento
    AND d.id_prop_despesa = u.id
WHERE
    d.pago = 'N'
    AND d.data < '2099-12-31'
    AND u.id = %s
    AND u.documento = %s;
"""

not_payed_expenses_ids_query = """
SELECT
    d.id
FROM
    despesas AS d
INNER JOIN
    contas ON contas.nome_conta = d.id_conta
    AND contas.id_prop_conta = d.id_prop_despesa
    AND contas.doc_prop_conta = d.doc_prop_despesa
INNER JOIN
    usuarios ON d.doc_prop_despesa = usuarios.documento
    AND d.id_prop_despesa = usuarios.id
WHERE
    d.pago = 'N'
    AND d.data < '2099-12-31'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

expenses_statement_query = """
SELECT
    d.descricao,
    d.valor,
    d.data,
    d.horario,
    d.categoria,
    c.nome_conta
FROM
    despesas AS d
INNER JOIN
    contas AS c
    ON d.id_conta = c.id
    AND d.id_prop_despesa = c.id_prop_conta
INNER JOIN
    usuarios AS u
    ON d.id_prop_despesa = u.id
    AND d.doc_prop_despesa = u.documento
WHERE
    d.pago = 'S'
    AND d.categoria <> 'Outros'
    AND d.data >= %s
    AND d.data <= %s
    AND c.nome_conta IN %s
    AND d.valor > 0
    AND u.id = %s
    AND u.documento = %s;
"""

get_id_query = """
SELECT
    d.id
FROM
    despesas AS d
INNER JOIN
    contas AS c
    ON c.id = d.id_conta
WHERE
    d.descricao = %s
    AND d.valor = %s
    AND d.data = %s
    AND d.horario = %s
    AND d.categoria = %s
    AND c.nome_conta = %s;
"""

update_not_payed_query = """
UPDATE
    despesas
SET
    data = %s,
    pago = "S"
WHERE
    id = %s;
"""

insert_expense_query = """
INSERT INTO
    despesas (
        descricao,
        valor,
        data,
        horario,
        categoria,
        id_conta,
        id_prop_despesa,
        doc_prop_despesa,
        pago
    )
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

expense_detailed_id_query = """
SELECT
    d.id
FROM
    despesas AS d
INNER JOIN usuarios AS u
    ON d.id_prop_despesa = u.id
    AND d.doc_prop_despesa = u.documento
WHERE
    d.data = %s
    AND d.id_conta = %s
    AND d.valor = %s
    AND u.id = %s
    AND u.documento = %s;
"""
