revenues_statement_query = """
SELECT
    r.descricao,
    r.valor,
    r.data,
    r.horario,
    r.categoria,
    c.nome_conta
FROM
    receitas AS r
INNER JOIN
    contas AS c
    ON r.id_conta = c.id
    AND r.id_prop_receita = c.id_prop_conta
INNER JOIN
    usuarios AS u
    ON r.id_prop_receita = u.id
    AND r.doc_prop_receita = u.documento
WHERE
    r.recebido = 'S'
    AND r.categoria <> 'Transferência recebida'
    AND r.data >= %s
    AND r.data <= %s
    AND r.valor > 0
    AND c.nome_conta IN %s
    AND u.id = %s
    AND u.documento = %s;
"""

total_account_revenue_query: str = """
SELECT
    COALESCE(CAST(SUM(r.valor) AS DECIMAL (10, 2)), 0)
FROM
    receitas AS r
INNER JOIN
    usuarios AS u
    ON r.id_prop_receita = u.id
    AND r.doc_prop_receita = u.documento
WHERE
    r.recebido = 'S'
    AND r.id_conta = %s
    AND u.id = %s
    AND u.documento = %s;
"""

not_received_revenue_query = """
SELECT
    r.id,
    r.descricao,
    r.valor,
    r.data,
    r.horario,
    r.categoria,
    c.nome_conta
FROM
    receitas AS r
INNER JOIN
    contas AS c
    ON c.id = r.id_conta
    AND c.id_prop_conta = r.id_prop_receita
    AND c.doc_prop_conta = r.doc_prop_receita
INNER JOIN
    usuarios
    ON r.doc_prop_receita = usuarios.documento
    AND r.id_prop_receita = usuarios.id
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
    contas ON contas.nome_conta = r.id_conta
    AND contas.id_prop_conta = r.id_prop_receita
    AND contas.doc_prop_conta = r.doc_prop_receita
INNER JOIN
    usuarios ON r.doc_prop_receita = usuarios.documento
    AND r.id_prop_receita = usuarios.id
WHERE
    r.recebido = 'N'
    AND r.data < '2099-12-31'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

most_categories_revenues_query: str = """
SELECT
    COALESCE(CAST(SUM(r.valor) AS DECIMAL (10 , 2 )), 0),
    r.categoria
FROM
    receitas AS r
INNER JOIN
    contas ON r.id_conta = contas.id
    AND r.id_prop_receita = contas.id_prop_conta
    AND r.doc_prop_receita = contas.doc_prop_conta
INNER JOIN
    usuarios ON r.id_prop_receita = usuarios.id
        AND r.doc_prop_receita = usuarios.documento
WHERE
    r.categoria <> 'Ajuste'
    AND contas.id_tipo_conta IN (
        SELECT
            id
        FROM
            tipos_conta
        WHERE
            nome IN (
            'Conta Corrente',
            'Conta Salário',
            'Vale Alimentação'
        )
    )
    AND usuarios.id = %s
    AND usuarios.documento = %s
GROUP BY r.categoria;"""

last_revenue_query: str = """
SELECT
    r.descricao AS 'Descrição',
    r.valor AS Valor,
    r.data AS Data,
    r.categoria AS Categoria,
    contas.nome_conta AS Conta
FROM
    receitas AS r
INNER JOIN
    contas ON r.id_conta = contas.id
    AND r.id_prop_receita = contas.id_prop_conta
    AND r.doc_prop_receita = contas.doc_prop_conta
INNER JOIN
    usuarios ON r.id_prop_receita = usuarios.id
        AND r.doc_prop_receita = usuarios.documento
WHERE
    r.categoria NOT IN (
        'Pix' ,
        'TED',
        'DOC',
        'Ajuste'
    )
    AND r.data <= %s
    AND usuarios.id = %s
    AND usuarios.documento = %s
    AND r.valor > 0
    AND r.recebido = 'S'
ORDER BY
    r.data DESC,
    r.id DESC
LIMIT 5;
"""

total_revenue_query: str = """
SELECT
    CAST(SUM(r.valor) AS DECIMAL (10 , 2 ))
FROM
    receitas AS r
INNER JOIN
    usuarios ON r.id_prop_receita = usuarios.id
    AND r.doc_prop_receita = usuarios.documento
INNER JOIN
    contas ON r.id_conta = contas.id
    AND r.id_prop_receita = contas.id_prop_conta
    AND r.doc_prop_receita = contas.doc_prop_conta
WHERE
    r.recebido = 'S'
    AND contas.id_tipo_conta NOT IN ('Fundo de Garantia', 'Vale Alimentação')
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

accounts_revenue_query: str = """
SELECT
    CAST(SUM(r.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    receitas AS r
INNER JOIN
    contas AS c
    ON r.id_conta = c.id
    AND r.id_prop_receita = c.id_prop_conta
    AND r.doc_prop_receita = c.doc_prop_conta
INNER JOIN
    usuarios AS u
    ON r.id_prop_receita = u.id
    AND r.doc_prop_receita = u.documento
WHERE
    r.data <= %s
    AND r.recebido = 'S'
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
        AND u.id = %s
        AND u.documento = %s
GROUP BY c.nome_conta
ORDER BY c.nome_conta ASC;
"""

future_accounts_revenue_query: str = """
SELECT
    CAST(SUM(r.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    receitas AS r
INNER JOIN
    contas AS c
    ON r.id_conta = c.id
    AND r.id_prop_receita = c.id_prop_conta
    AND r.doc_prop_receita = c.doc_prop_conta
INNER JOIN
    usuarios ON r.id_prop_receita = usuarios.id
    AND r.doc_prop_receita = usuarios.documento
WHERE
    r.recebido = 'N'
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

max_revenue_query: str = """
SELECT
    r.descricao AS 'Descrição',
    r.valor AS 'Valor',
    r.data AS 'Data',
    r.categoria AS 'Categoria',
    c.nome_conta AS 'Conta'
FROM
    receitas AS r
INNER JOIN
    contas AS c
    ON r.id_conta = c.id
    AND r.id_prop_receita = c.id_prop_conta
    AND r.doc_prop_receita
    AND c.doc_prop_conta
INNER JOIN
    usuarios AS u
    ON r.id_prop_receita = u.id
    AND r.doc_prop_receita = u.documento
WHERE
    r.categoria NOT IN (
        'Ajuste',
        'DOC',
        'Pix',
        'TED'
    )
    AND r.data <= %s
    AND u.id = %s
    AND u.documento = %s
    AND r.valor > 0
ORDER BY
    r.valor DESC
LIMIT 5;
"""

last_revenue_id_query: str = """
SELECT id FROM receitas ORDER BY id DESC LIMIT 1;
"""

ticket_revenue_query: str = """
SELECT
    COALESCE(CAST(SUM(r.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    receitas AS r
INNER JOIN
    contas ON r.id_conta = contas.id
    AND r.id_prop_receita = contas.id_prop_conta
    AND r.doc_prop_receita = contas.doc_prop_conta
    INNER JOIN
    usuarios ON r.id_prop_receita = usuarios.id
        AND r.doc_prop_receita = usuarios.documento
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
    AND r.recebido = 'S'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

fund_revenue_query: str = """
SELECT
    COALESCE(CAST(SUM(r.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    receitas AS r
INNER JOIN
    contas ON r.id_conta = contas.id
    AND r.id_prop_receita = contas.id_prop_conta
    AND r.doc_prop_receita = contas.doc_prop_conta
INNER JOIN
    usuarios ON r.id_prop_receita = usuarios.id
        AND r.doc_prop_receita = usuarios.documento
WHERE
    contas.id_tipo_conta IN (
        SELECT
            id
        FROM
            tipos_conta
        WHERE
            nome = 'Fundo de Garantia'
    )
    AND r.recebido = 'S'
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

insert_revenue_query = '''
INSERT INTO
    receitas (
        descricao,
        valor,
        data,
        horario,
        categoria,
        id_conta,
        id_prop_receita,
        doc_prop_receita,
        recebido
    )
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
'''

update_not_received_query = """
UPDATE
    receitas
SET
    data = %s,
    recebido = "S"
WHERE id = %s;
"""

get_revenue_id_query = """
SELECT
    r.id
FROM
    receitas AS r
INNER JOIN
    contas AS c
    ON c.id = r.id_conta
WHERE
    r.descricao = %s
    AND r.valor = %s
    AND r.data = %s
    AND r.horario = %s
    AND r.categoria = %s
    AND c.nome_conta = %s;
"""
