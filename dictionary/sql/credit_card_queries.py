credit_card_expire_date_query = """
SELECT
    cc.data_validade
FROM
    cartao_credito AS cc
WHERE
    cc.doc_titular_cartao = %s
    AND cc.nome_cartao = %s
    AND cc.id_prop_cartao = %s;
"""

owner_cards_query = """
SELECT
    cc.nome_cartao
FROM
    cartao_credito AS cc
INNER JOIN
    usuarios AS u
    ON cc.id_prop_cartao = u.id
    AND cc.doc_titular_cartao = u.documento
WHERE
    u.id = %s
    AND u.documento = %s;
"""

credit_card_id_query = """
SELECT
    cc.id
FROM
    cartao_credito AS cc
INNER JOIN
    usuarios AS u
    ON cc.id_prop_cartao = u.id
    AND cc.doc_titular_cartao = u.documento
WHERE
    u.id = %s
    AND u.documento = %s
    AND cc.nome_cartao = %s;
"""

owner_active_cards_query = """
SELECT
    cc.id
FROM
    cartao_credito AS cc
INNER JOIN
    usuarios AS u
    ON cc.id_prop_cartao = u.id
    AND cc.doc_titular_cartao = u.documento
WHERE
    u.id = %s
    AND u.documento = %s
    AND cc.inativo = 'N';
"""

card_invoices_query = """
SELECT
    CONCAT(fc.mes, " de ", fc.ano)
FROM
    fechamentos_cartao AS fc
INNER JOIN
    cartao_credito AS cc
    ON fc.id_cartao = cc.id
    AND fc.numero_cartao = cc.numero_cartao
INNER JOIN
    usuarios AS u
    ON u.documento = fc.doc_prop_cartao
WHERE
    fc.id_cartao IN(
        SELECT
            cc.id
        FROM
            cartao_credito AS cc
        WHERE
            cc.nome_cartao = %s
            AND cc.id_prop_cartao = %s
            AND cc.doc_titular_cartao = %s
    )
    AND u.id = %s
    AND u.documento = %s
    AND fc.fechado = 'N'
ORDER BY
    fc.data_comeco_fatura;
"""

card_invoices_id_query = """
SELECT
    COUNT(fc.id)
FROM
    fechamentos_cartao AS fc
INNER JOIN
    cartao_credito AS cc
    ON fc.id_cartao = cc.id
    AND fc.numero_cartao = cc.numero_cartao
INNER JOIN
    usuarios
    ON usuarios.documento = fc.doc_prop_cartao
WHERE
    cc.id IN %s
    AND usuarios.id = %s
    AND usuarios.documento = %s;
"""

new_credit_card_query = """
INSERT INTO
    cartao_credito (
        nome_cartao,
        numero_cartao,
        nome_titular,
        id_prop_cartao,
        doc_titular_cartao,
        data_validade,
        codigo_seguranca,
        limite_credito,
        limite_maximo,
        id_conta_associada
    )
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
);"""

cc_max_limit_query = '''
SELECT
    limite_maximo
FROM
    cartao_credito
WHERE
    nome_cartao = %s
    AND proprietario_cartao = %s
    AND doc_prop_cartao = %s
'''

new_limit_query = '''
UPDATE
    cartao_credito
SET
    limite_credito = %s,
    inativo = %s
WHERE
    id = %s
    AND proprietario_cartao = %s
    AND doc_prop_cartao = %s;
'''

new_credit_card_invoice_query = """
INSERT INTO
    fechamentos_cartao (
        id_cartao,
        numero_cartao,
        id_prop_cartao,
        doc_prop_cartao,
        ano,
        mes,
        data_comeco_fatura,
        data_fim_fatura
    )
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

credit_card_name_query = """
SELECT
    cc.nome_cartao
FROM
    cartao_credito AS cc
INNER JOIN
    usuarios AS u
    ON cc.id_prop_cartao = u.id
    AND cc.doc_titular_cartao = u.documento
WHERE
    cc.id = %s
    AND u.id = %s
    AND u.documento = %s;
"""
