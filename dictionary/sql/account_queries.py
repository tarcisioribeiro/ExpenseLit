unique_account_id_query = """
SELECT
    c.id
FROM
    contas AS c
INNER JOIN
    usuarios AS u ON u.id = c.id_prop_conta
    AND u.documento = c.doc_prop_conta
WHERE
    c.nome_conta = %s
    AND u.id = %s
    AND u.documento = %s;
"""

account_image_query = """
SELECT
    c.caminho_imagem
FROM
    contas AS c
INNER JOIN
    usuarios AS u
    ON c.doc_prop_conta = u.documento
    AND c.id_prop_conta = u.id
WHERE
    c.nome_conta = %s
    AND u.id = %s
    AND u.documento = %s;
"""

user_fund_accounts_query = """
SELECT
    c.nome_conta
FROM
    contas AS c
INNER JOIN
    usuarios AS u
    ON c.id_prop_conta = u.id
    AND c.doc_prop_conta = u.documento
WHERE
    c.id_tipo_conta IN (
        SELECT
            id
        FROM
            tipos_conta
        WHERE
            nome = 'Fundo de Garantia'
    )
    AND c.inativa = 'N'
    AND u.id = %s
    AND u.documento = %s;
"""

user_current_accounts_query = """
SELECT
    c.nome_conta
FROM
    contas AS c
INNER JOIN usuarios AS u
    ON c.id_prop_conta = u.id
    AND c.doc_prop_conta = u.documento
WHERE
    c.id_tipo_conta IN (
    SELECT
        id
    FROM
        tipos_conta
    WHERE
        nome = 'Conta Corrente'
    )
    AND c.inativa = 'N'
    AND u.id = %s
    AND u.documento = %s;
"""

user_all_current_accounts_query = """
SELECT
    c.nome_conta
FROM
    contas AS c
INNER JOIN
    usuarios AS u
    ON c.id_prop_conta = u.id
    AND c.doc_prop_conta = u.documento
WHERE
    u.id = %s
    AND u.documento = %s;
"""

current_accounts_query: str = """
SELECT DISTINCT
    (c.nome_conta)
FROM
    contas AS c
INNER JOIN
    usuarios AS u
WHERE
    c.inativa = 'N'
    AND c.id_prop_conta = u.id
    AND c.doc_prop_conta = u.documento
    AND c.id_tipo_conta NOT IN (
        SELECT
            id
        FROM
            tipos_conta
        WHERE
            nome = 'Fundo de Garantia'
    )
    AND u.id = %s
    AND u.documento = %s
ORDER BY
    c.nome_conta ASC;
"""

accounts_name_query: str = """
SELECT DISTINCT
    (c.nome_conta)
FROM
    contas AS c
INNER JOIN
    usuarios AS u
WHERE
    c.inativa = 'N'
    AND c.id_prop_conta = u.id
    AND c.doc_prop_conta = u.documento
    AND u.id = %s
    AND u.documento = %s
    AND c.id = %s;
"""

selected_card_linked_account_query = """
SELECT
    DISTINCT(cc.id_conta_associada)
FROM
    contas AS c
INNER JOIN
    cartao_credito AS cc
    ON c.id_prop_conta = cc.id_prop_cartao
    AND c.doc_prop_conta = cc.doc_titular_cartao
WHERE
    cc.nome_cartao = %s
    AND c.id_prop_conta = %s
    AND c.doc_prop_conta = %s;
"""

insert_account_query = """
INSERT INTO
    contas (
        nome_conta,
        id_tipo_conta,
        id_prop_conta,
        doc_prop_conta,
        caminho_imagem
    )
VALUES (%s, %s, %s, %s, %s);
"""

update_account_query = '''
UPDATE
    contas
SET
    inativa = %s,
    tipo_conta = %s
WHERE
    nome_conta = %s
    AND id_prop_conta = %s
    AND doc_prop_conta = %s;
'''
