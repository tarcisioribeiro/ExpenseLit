benefited_quantity_query = """
SELECT
    COUNT(b.id)
FROM
    beneficiados AS b
INNER JOIN
    usuarios AS u
    ON b.id <> u.id
    AND b.documento <> u.documento
WHERE
    u.id = %s
    AND u.documento = %s;
"""

beneficiaries_query = """
SELECT
    b.nome
FROM
    beneficiados AS b
INNER JOIN usuarios AS u
    ON b.nome <> u.nome
    AND b.documento <> u.documento
WHERE
    u.id = %s
    AND u.documento = %s;
"""

insert_benefited_query = '''
INSERT INTO
    beneficiados (
        `nome`,
        `documento`,
        `telefone`
    )
VALUES (%s, %s, %s);
'''

is_new_benefited_name_valid_query = """
SELECT
    COUNT(id)
FROM
    beneficiados
WHERE
    nome = %s
    AND id <> %s;
"""

is_new_benefited_document_valid_query = """
SELECT
    COUNT(id)
FROM
    beneficiados
WHERE
    documento = %s
    AND id <> %s;
"""

is_new_benefited_phone_valid_query = """
SELECT
    COUNT(id)
FROM
    beneficiados
WHERE
    telefone = %s
    AND id <> %s;
"""

is_entire_benefited_data_valid_query = """
SELECT
    COUNT(id)
FROM
    beneficiados
WHERE
    nome = %s
    AND documento = %s
    AND telefone = %s;
"""

beneficiaries_complete_data_query = """
SELECT
    b.id,
    b.nome,
    b.documento,
    b.telefone
FROM
    beneficiados AS b
INNER JOIN
    usuarios AS u
    ON b.id <> u.id
    AND b.documento <> u.documento
WHERE
    u.id = %s
    AND u.documento = %s
    AND b.nome = %s;
"""

get_loans_ids_query = """
SELECT
    id
FROM
    emprestimos
WHERE
    id_beneficiado = %s
    AND doc_beneficiado = %s;
"""

new_benefited_loans_data_query = """
UPDATE
    emprestimos
SET
    id_beneficiado = %s,
    doc_beneficiado = %s
WHERE
    id_beneficiado = %s
    AND doc_beneficiado = %s
    AND id IN %s;
"""

new_benefited_data_query = """
UPDATE
    beneficiados
SET
    nome = %s,
    documento = %s,
    telefone = %s
WHERE
    id = %s;
"""

new_benefited_query = """
INSERT INTO beneficiados (
    nome,
    documento,
    telefone
)
VALUES (%s, %s, %s);
"""

benefited_doc_name_query = """
SELECT
    b.nome,
    b.documento
FROM
    beneficiados AS b
WHERE
    b.nome = %s;
"""

choosed_benefited_id_query = """
SELECT
    b.id
FROM
    beneficiados AS b
WHERE
    b.nome = %s
    AND b.documento = %s;
"""
