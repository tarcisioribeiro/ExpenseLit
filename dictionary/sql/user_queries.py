user_id_query = """
SELECT
    u.id
FROM
    usuarios AS u
WHERE
    u.login = %s
    AND u.senha = %s;
"""

check_user_query = """
SELECT
    COUNT(u.id)
FROM
    usuarios AS u;
"""

check_if_user_login_exists_query = """
SELECT
    COUNT(u.id)
FROM
    usuarios AS u
WHERE
    u.login = %s;
"""

user_real_name_query = """
SELECT
    u.nome
FROM
    usuarios AS u
INNER JOIN
    usuarios_logados AS ul
    ON u.id = ul.id_usuario
WHERE
    u.id = %s
    AND u.documento = %s
GROUP BY u.id;
"""

insert_new_user_query = """
INSERT INTO
    usuarios (
        login,
        senha,
        nome,
        documento,
        telefone,
        email,
        sexo
    )
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

document_exists_query = """
SELECT
    COUNT(u.id)
FROM
    usuarios AS u
WHERE
    u.documento = %s;
"""

user_login_query = """
SELECT
    u.id, u.documento
FROM
    usuarios AS u
INNER JOIN
    usuarios_logados AS ul
    ON u.id = ul.id_usuario
WHERE ul.sessao_id = %s;
"""

user_data_query = """
SELECT
    u.id,
    u.nome,
    u.documento
FROM
    usuarios AS u
WHERE u.login = %s
    AND u.senha = %s;
"""

name_query = """
SELECT
    u.nome
FROM
    usuarios AS u
WHERE
    u.id = %s
AND
    u.documento = %s;
"""
sex_query = """
SELECT
    u.sexo
FROM
    usuarios AS u
WHERE
    u.id = %s
    AND u.documento = %s;
"""

count_users_query = """
SELECT
    COUNT(u.id)
FROM
    usuarios AS u
WHERE
    u.login = %s
    AND u.senha = %s;
"""

password_query = """
SELECT
    u.senha
FROM
    usuarios AS u
WHERE
    u.login = %s;
"""
