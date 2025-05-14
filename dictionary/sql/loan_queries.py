debtors_query: str = """
SELECT
    b.nome
FROM
    emprestimos AS e
INNER JOIN
    beneficiados AS b
    ON e.id_beneficiado = b.id
    AND e.doc_beneficiado = b.documento
INNER JOIN
    credores AS c
    ON e.id_credor = c.id
    AND e.doc_credor = c.documento
INNER JOIN
    usuarios AS u
    ON e.id_credor = u.id
    AND e.doc_credor = u.documento
WHERE
    e.pago = 'N'
    AND u.id = %s
    AND u.documento = %s
GROUP BY e.id_beneficiado;
"""

loan_description_query = """
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
    COALESCE(SUM(e.valor - e.valor_pago), 0)
FROM
    emprestimos AS e
INNER JOIN
    beneficiados AS b
    ON e.id_beneficiado = b.id
    AND e.doc_beneficiado = b.documento
INNER JOIN
    credores AS c
    ON e.id_credor = c.id
    AND e.doc_credor = c.documento
INNER JOIN
    usuarios AS u
    ON e.id_credor = u.id
    AND e.doc_credor = u.documento
WHERE
    e.id_beneficiado = %s
    AND u.id = %s
    AND u.documento = %s
    AND pago = 'N';
"""

not_payed_loans_query = """
SELECT
    e.id AS 'ID',
    e.descricao AS 'Descrição',
    e.valor AS 'Valor',
    e.valor_pago AS 'Valor Pago',
    e.valor - e.valor_pago AS 'Valor a Pagar',
    e.data AS 'Data',
    e.categoria AS 'Categoria',
    c.nome_conta AS 'Conta',
    cr.nome AS 'Credor'
FROM
    emprestimos AS e
INNER JOIN usuarios AS u
    ON e.id_beneficiado = u.id
    AND e.doc_beneficiado = u.documento
INNER JOIN
    credores AS cr
    ON cr.documento <> u.documento
    AND cr.documento = e.doc_credor
    AND cr.nome <> u.nome
    AND cr.documento <> e.doc_beneficiado
    AND cr.id = e.id_credor
INNER JOIN
    contas AS c
    ON c.id_prop_conta = e.id_beneficiado
    AND c.doc_prop_conta = e.doc_beneficiado
    AND c.id = e.id_conta
INNER JOIN
    beneficiados as b
    ON b.id = e.id_beneficiado
    AND b.documento = e.doc_beneficiado
    AND b.documento = u.documento
WHERE
    u.id = %s
    AND u.documento = %s
    AND pago = 'N'
    AND valor_pago < valor;
"""

not_received_loans_query = """
SELECT
    e.id AS 'ID',
    e.descricao AS 'Descrição',
    e.valor AS 'Valor',
    e.valor_pago AS 'Valor Pago',
    e.valor - e.valor_pago AS 'Valor a Pagar',
    e.data AS 'Data',
    e.categoria AS 'Categoria',
    c.nome_conta AS 'Conta',
    b.nome AS 'Devedor'
FROM
    emprestimos AS e
INNER JOIN usuarios AS u
    ON e.id_credor = u.id
    AND e.doc_credor = u.documento
INNER JOIN contas AS c
    ON c.id = e.id_conta
    AND c.id_prop_conta = e.id_credor
    AND c.doc_prop_conta = e.doc_credor
    AND c.id_prop_conta = u.id
    AND c.doc_prop_conta = u.documento
INNER JOIN beneficiados as b
    ON b.id = e.id_beneficiado
    AND b.documento = e.doc_beneficiado
    AND b.documento <> u.documento
WHERE
    u.id = %s
    AND u.documento = %s
    AND pago = 'N';
"""

last_loan_id_query: str = """
SELECT id FROM emprestimos ORDER BY id DESC LIMIT 1;
"""

loan_expense_query: str = """
SELECT
    COALESCE(CAST(SUM(
        e.valor - e.valor_pago
    ) AS DECIMAL(10, 2)), 0)
FROM
    emprestimos AS e
INNER JOIN
    usuarios AS u
    ON e.id_credor = u.id
    AND e.doc_credor = u.documento
WHERE
    e.pago = 'N'
    AND u.id = %s
    AND u.documento = %s;
"""

debts_expense_query: str = """
SELECT
    COALESCE(CAST(SUM(
        e.valor - e.valor_pago
    ) AS DECIMAL (10 , 2 )), 0)
FROM
    emprestimos AS e
INNER JOIN
    usuarios AS u
    ON e.id_beneficiado = u.id
    AND e.doc_beneficiado = u.documento
WHERE
    e.pago = 'N'
        AND u.id = %s
        AND u.documento = %s;
"""

insert_loan_query = '''
INSERT INTO
    emprestimos (
        descricao,
        valor,
        valor_pago,
        data,
        horario,
        categoria,
        id_conta,
        id_beneficiado,
        doc_beneficiado,
        id_credor,
        doc_credor,
        pago
    )
VALUES (
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s
);
'''

update_debt_query = '''
UPDATE
    emprestimos
SET
    valor_pago = %s,
    pago = %s
WHERE
    descricao = %s
    AND pago = %s
    AND id_beneficiado = %s
    AND doc_beneficiado = %s;
'''

update_loan_query = '''
UPDATE
    emprestimos
SET
    valor_pago = %s,
    pago = %s
WHERE
    descricao = %s
    AND pago = %s
    AND id_credor = %s
    AND doc_credor = %s;
'''

total_actual_value_query = '''
SELECT
    DISTINCT(e.valor)
FROM
    emprestimos AS e
INNER JOIN contas AS c
    ON c.id_prop_conta = e.id_beneficiado
    AND c.doc_prop_conta = e.doc_beneficiado
INNER JOIN usuarios AS u
    ON u.id = e.id_beneficiado
    AND u.documento = e.doc_beneficiado
WHERE
    e.pago = 'N'
    AND e.descricao = %s;
'''

payed_actual_value_query = '''
SELECT
    DISTINCT(e.valor_pago)
FROM
    emprestimos AS e
    INNER JOIN contas AS c
    ON c.id_prop_conta = e.id_beneficiado
    AND c.doc_prop_conta = e.doc_beneficiado
INNER JOIN usuarios AS u
    ON u.id = e.id_beneficiado
    AND u.documento = e.doc_beneficiado
WHERE
    e.pago = 'N'
    AND e.id = %s;
'''

paying_max_value_query = '''
SELECT
    DISTINCT(e.valor - e.valor_pago)
FROM
    emprestimos AS e
INNER JOIN
    contas AS c
    ON c.id_prop_conta = e.id_beneficiado
    AND c.doc_prop_conta = e.doc_beneficiado
INNER JOIN
    usuarios AS u
    ON
    u.id = e.id_beneficiado
    AND u.documento = e.doc_beneficiado
WHERE
    e.pago = 'N'
    AND e.id = %s;
'''


receiving_max_value_query = '''
SELECT
    DISTINCT(e.valor - e.valor_pago)
FROM
    emprestimos AS e
INNER JOIN
contas AS c ON
    c.id_prop_conta = e.id_credor
    AND c.doc_prop_conta = e.doc_credor
INNER JOIN
    usuarios AS u
    ON u.id = e.id_credor
    AND u.documento = e.doc_credor
WHERE
    e.pago = 'N'
    AND e.id = %s;
'''

received_actual_value_query = '''
SELECT
    DISTINCT(e.valor_pago)
FROM
    emprestimos AS e
INNER JOIN
    contas AS c ON
    c.id_prop_conta = e.id_credor
    AND c.doc_prop_conta = e.doc_credor
INNER JOIN
    usuarios AS u
    ON u.id = e.id_credor
    AND u.documento = e.doc_credor
WHERE
    e.pago = 'N'
    AND e.id = %s;
'''

total_actual_value_query = '''
SELECT
    e.valor
FROM
    emprestimos AS e
INNER JOIN
    usuarios AS u
    ON u.documento <> e.doc_credor
WHERE
    e.pago = 'N'
    AND e.id = %s;
'''

total_loan_actual_value_query = '''
SELECT
    e.valor
FROM
    emprestimos AS e
INNER JOIN
    usuarios AS u
    ON u.documento = e.doc_credor
WHERE
    e.pago = 'N'
    AND e.id = %s
    AND u.id = %s
    AND u.documento = %s;
'''
