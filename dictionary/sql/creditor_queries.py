creditors_quantity_query = """
SELECT
    COUNT(c.id)
FROM
    credores AS c
INNER JOIN
    usuarios AS u
    ON c.documento <> u.documento
    AND c.nome <> u.nome
WHERE
    u.id = %s
    AND u.documento = %s;
"""

creditors_names_query = """
SELECT
    c.nome
FROM
    credores AS c
INNER JOIN usuarios AS u
    ON c.id <> u.id
    AND c.documento <> u.documento
WHERE
    u.id = %s
    AND u.documento = %s;
]"""

creditors_complete_data_query = """
SELECT
    c.id,
    c.documento,
    c.telefone
FROM
    credores AS c
INNER JOIN
    usuarios AS u
    ON c.id <> u.id
    AND c.documento <> u.documento
WHERE
    u.id = %s
    AND u.documento = %s
    AND c.nome = %s;
"""

get_loans_creditor_ids_query = """
SELECT
    id
FROM
    emprestimos
WHERE
    credor = %s
    AND documento_credor = %s;
"""

is_entire_creditor_data_valid_query = """
SELECT
    COUNT(id_credor)
FROM
    credores
WHERE
    nome = %s
    AND documento = %s
    AND telefone = %s;
"""

is_new_creditor_phone_valid_query = """
SELECT
    COUNT(id_credor)
FROM
    credores
WHERE
    telefone = %s
    AND id_credor <> %s;
"""

is_new_creditor_name_valid_query = """
SELECT
    COUNT(id_credor)
FROM
    credores
WHERE
    nome = %s
    AND id_credor <> %s;
"""

is_new_creditor_document_valid_query = """
SELECT
    COUNT(id_credor)
FROM
    credores
WHERE
    documento = %s
    AND id_credor <> %s;
"""

new_creditor_loans_data_query = """
UPDATE
    emprestimos
SET
    credor = %s,
    documento_credor = %s
WHERE credor = %s
    AND documento_credor = %s
    AND id_emprestimo IN %s;
"""

new_creditor_data_query = """
UPDATE
    credores
SET
    nome = %s,
    documento = %s,
    telefone = %s
    WHERE id_credor = %s;
"""

insert_creditor_query = '''
INSERT INTO
    credores (
        `nome`,
        `documento`,
        `telefone`
    )
VALUES (%s, %s, %s);'''


creditor_doc_name_query = """
SELECT
    c.nome,
    c.documento
FROM
    credores AS c
INNER JOIN usuarios AS u
    ON c.documento = u.documento
WHERE
    u.id = %s
    AND u.documento = %s;
"""
