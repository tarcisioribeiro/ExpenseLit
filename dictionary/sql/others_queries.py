log_query = '''
INSERT INTO
    logs_atividades (
    id_usuario_log,
    tipo_log,
    conteudo_log
)
VALUES
( %s, %s, %s);
'''

register_session_query = """
INSERT INTO
    usuarios_logados (
        id_usuario,
        doc_usuario,
        nome_completo,
        sessao_id
    )
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    data_login = CURRENT_TIMESTAMP, sessao_id = VALUES(sessao_id);
"""

months_query = '''SELECT nome_mes FROM meses;'''

account_models_query = '''
SELECT
    tc.id,
    mc.nome_instituicao
FROM
    modelos_conta AS mc
INNER JOIN
    tipos_conta AS tc
    ON tc.id = mc.id_tipo
ORDER BY
    mc.id;
'''

years_query = '''SELECT ano FROM anos;'''

get_actual_month_query = """
SELECT
    nome_mes
FROM
    meses
WHERE
    id = %s;
"""

delete_session_query = """
DELETE
    ul
FROM
    usuarios_logados AS ul
INNER JOIN usuarios AS u
    ON ul.id_usuario = u.id
WHERE
    u.id = %s
    AND u.documento = %s;
"""

accounts_type_query = """
SELECT
    nome
FROM
    tipos_conta;
"""

expense_categories_query = """
SELECT
    nome
FROM
    categorias_despesa;
"""

revenue_categories_query = """
SELECT
    nome
FROM
    categorias_receita;
"""

transfer_categories_query = """
SELECT
    nome
FROM
    categorias_transferencia;
"""

time_query = """
SELECT
    CURTIME();
"""
