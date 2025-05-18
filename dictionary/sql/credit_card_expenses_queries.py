credit_card_next_expenses_query: str = """
SELECT
    COALESCE(SUM(dcc.valor), 0)
FROM
    despesas_cartao_credito AS dcc
INNER JOIN
    fechamentos_cartao AS fc
    ON dcc.numero_cartao = fc.numero_cartao
        AND dcc.doc_prop_cartao = fc.doc_prop_cartao
INNER JOIN
        usuarios AS u
        ON dcc.id_prop_despesa_cartao = u.id
        AND dcc.doc_prop_cartao = u.documento
WHERE
    dcc.id_cartao = %s
    AND dcc.pago = 'N'
    AND dcc.data > fc.data_fim_fatura
    AND fc.ano = %s
    AND fc.mes = %s
    AND u.id = %s
    AND u.documento = %s;
"""

most_credit_card_expenses_query: str = """
SELECT
    COALESCE(CAST(SUM(dcc.valor) AS DECIMAL (10 , 2 )), 0),
    dcc.categoria
FROM
    despesas_cartao_credito AS dcc
INNER JOIN
    cartao_credito AS cc
    ON dcc.doc_prop_cartao = cc.doc_titular_cartao
        AND dcc.numero_cartao = cc.numero_cartao
INNER JOIN
    usuarios AS u
    ON dcc.id_prop_despesa_cartao = u.id
    AND dcc.doc_prop_cartao = u.documento
WHERE
    dcc.categoria <> 'Ajuste'
    AND u.id = %s
    AND u.documento = %s
GROUP BY dcc.categoria;
"""

last_credit_card_expense_id_query: str = """
SELECT id FROM despesas_cartao_credito ORDER BY id DESC LIMIT 1;
"""

credit_card_id_expenses_query = """
SELECT
    dcc.id
FROM
    despesas_cartao_credito AS dcc
INNER JOIN
    fechamentos_cartao AS fc
    ON dcc.numero_cartao = fc.numero_cartao
    AND dcc.doc_prop_cartao = fc.doc_prop_cartao
    AND dcc.id_prop_despesa_cartao = fc.id_prop_cartao
INNER JOIN
    usuarios AS u
    ON dcc.id_prop_despesa_cartao = u.id
    AND dcc.doc_prop_cartao = u.documento
WHERE
    dcc.id_cartao IN (
        SELECT
            cc.id
        FROM
            cartao_credito AS cc
        INNER JOIN
            usuarios AS u
            ON cc.id_prop_cartao = u.id
            AND cc.doc_titular_cartao = u.documento
        WHERE
            cc.nome_cartao = %s
            AND u.id = %s
            AND u.documento = %s
    )
    AND dcc.data >= fc.data_comeco_fatura
    AND dcc.data <= fc.data_fim_fatura
    AND fc.ano = %s
    AND fc.mes = %s
    AND u.id = %s
    AND u.documento = %s
    AND pago = 'N';
"""

month_query = '''
SELECT
    mes
FROM
    fechamentos_cartao
WHERE
    CURDATE()
BETWEEN
    data_comeco_fatura
AND
    data_fim_fatura
    AND id_cartao = %s
    AND doc_prop_cartao = %s
    AND id_prop_cartao = %s;
'''

credit_card_not_payed_expenses_query: str = """
SELECT
    COALESCE(SUM(dcc.valor), 0)
FROM
    despesas_cartao_credito AS dcc
INNER JOIN
    fechamentos_cartao AS fc
    ON dcc.numero_cartao = fc.numero_cartao
    AND dcc.doc_prop_cartao = fc.doc_prop_cartao
INNER JOIN
    usuarios AS u
    ON dcc.id_prop_despesa_cartao = u.id
    AND dcc.doc_prop_cartao = u.documento
WHERE
    dcc.id_cartao = %s
    AND dcc.data <= fc.data_comeco_fatura
    AND dcc.pago = 'N'
    AND fc.ano <= %s
    AND fc.mes = %s
    AND u.id = %s
    AND u.documento = %s;
"""

credit_card_month_expenses_query: str = """
SELECT
    COALESCE(SUM(dcc.valor), 0)
FROM
    despesas_cartao_credito AS dcc
INNER JOIN
    fechamentos_cartao AS fc
    ON dcc.numero_cartao = fc.numero_cartao
    AND dcc.doc_prop_cartao = fc.doc_prop_cartao
INNER JOIN usuarios AS u
    ON dcc.id_prop_despesa_cartao = u.id
    AND dcc.doc_prop_cartao = u.documento
WHERE
    dcc.id_cartao IN (
        SELECT
            cc.id
        FROM
            cartao_credito AS cc
        INNER JOIN
            usuarios AS u
            ON u.id = cc.id_prop_cartao
            AND u.documento = cc.doc_titular_cartao
        WHERE
            cc.id = %s
            AND u.id = %s
            AND u.documento = %s
    )
    AND dcc.data >= fc.data_comeco_fatura
    AND dcc.data <= fc.data_fim_fatura
    AND dcc.pago = 'N'
    AND fc.ano = %s
    AND fc.mes = %s
    AND u.id = %s
    AND u.documento = %s;
"""

credit_card_month_expenses_complete_query: str = """
SELECT
    dcc.descricao AS 'Descrição',
    dcc.valor AS 'Valor',
    dcc.data AS 'Data',
    dcc.categoria AS 'Categoria',
    CONCAT(dcc.parcela, 'ª') AS 'Parcela'
FROM
    despesas_cartao_credito AS dcc
INNER JOIN
    fechamentos_cartao AS fc
    ON dcc.numero_cartao = fc.numero_cartao
    AND dcc.doc_prop_cartao = fc.doc_prop_cartao
INNER JOIN
    usuarios AS u
    ON dcc.id_prop_despesa_cartao = u.id
    AND dcc.doc_prop_cartao = u.documento
INNER JOIN
    cartao_credito AS cc
    ON cc.doc_titular_cartao = dcc.doc_prop_cartao
    AND cc.id_prop_cartao = dcc.id_prop_despesa_cartao
WHERE
    cc.nome_cartao = %s
    AND dcc.data >= fc.data_comeco_fatura
    AND dcc.data <= fc.data_fim_fatura
    AND dcc.pago = 'N'
    AND fc.ano = %s
    AND fc.mes = %s
    AND u.id = %s
    AND u.documento = %s;
"""

credit_card_limit_query: str = """
SELECT
    COALESCE(SUM(cc.limite_credito), 0)
FROM
    cartao_credito AS cc
INNER JOIN
    usuarios AS u
    ON cc.doc_titular_cartao = u.documento
    AND cc.id_prop_cartao = u.id
WHERE
    cc.id = %s
    AND u.id = %s
    AND u.documento = %s;
"""

card_key_query = """
SELECT
    cc.id,
    cc.numero_cartao,
    cc.id_prop_cartao,
    cc.doc_titular_cartao,
    cc.codigo_seguranca
FROM
    cartao_credito AS cc
INNER JOIN usuarios AS u
    ON cc.id_prop_cartao = u.id
    AND cc.doc_titular_cartao = u.documento
WHERE
    cc.nome_cartao = %s
    AND u.id = %s
    AND u.documento = %s;
"""

invoices_quantity_query = """
SELECT
    COUNT(fc.id)
FROM
    fechamentos_cartao AS fc
INNER JOIN
    cartao_credito AS cc
    ON fc.doc_prop_cartao = cc.doc_titular_cartao
INNER JOIN
    usuarios AS u
    ON fc.doc_prop_cartao = u.documento
WHERE
    cc.id = %s
    AND cc.nome_cartao = %s
    AND u.id = %s
    AND u.documento = %s;
"""

card_associated_account_id_query = """
SELECT
    DISTINCT(cc.id_conta_associada)
FROM
    cartao_credito AS cc
INNER JOIN
    contas AS c
    ON c.id_prop_conta = cc.id_prop_cartao
    AND c.doc_prop_conta = cc.doc_titular_cartao
WHERE
    cc.id_prop_cartao = %s
    AND cc.doc_titular_cartao = %s
    AND cc.id = %s;
"""

card_account_name_query = """
SELECT
    c.nome_conta
FROM
    contas AS c
INNER JOIN
    cartao_credito AS cc
    On cc.id_prop_cartao = c.id_prop_conta
    AND cc.doc_titular_cartao = c.doc_prop_conta
    AND cc.id_conta_associada = c.id
INNER JOIN
    usuarios AS u
    ON c.id_prop_conta = u.id
    AND c.doc_prop_conta = u.documento
WHERE
    u.id = %s
    AND u.documento = %s
    AND cc.id_conta_associada = %s;
"""

credit_card_expense_query = """
INSERT INTO
    despesas_cartao_credito (
        descricao,
        valor,
        data,
        horario,
        categoria,
        id_cartao,
        numero_cartao,
        id_prop_despesa_cartao,
        doc_prop_cartao,
        parcela,
        pago)
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
    %s);
"""

update_invoice_query = '''
UPDATE
    fechamentos_cartao
SET fechado = 'S'
WHERE id_cartao IN(
    SELECT
        cc.id
    FROM
        cartao_credito AS cc
    WHERE
        cc.nome_cartao = %s
        AND cc.id_prop_cartao = %s
        AND cc.doc_titular_cartao = %s
    )
    AND mes = %s
    AND ano = %s
    AND id_prop_cartao = %s
    AND doc_prop_cartao = %s;
'''
