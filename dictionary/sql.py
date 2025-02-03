last_expense_query: str = """
SELECT 
    despesas.descricao AS 'Descrição',
    despesas.valor AS 'Valor',
    despesas.data AS 'Data',
    despesas.categoria AS 'Categoria',
    despesas.conta AS 'Conta'
FROM
    despesas
    INNER JOIN
    contas ON despesas.conta = contas.nome_conta AND despesas.proprietario_despesa = contas.proprietario_conta AND despesas.documento_proprietario_despesa = contas.documento_proprietario_conta
    INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome AND despesas.documento_proprietario_despesa = usuarios.cpf
WHERE
    despesas.categoria NOT IN ('Pix', 'TED', 'DOC', 'Ajuste')
        AND despesas.descricao NOT IN('Aporte Inicial','Placeholder','Teste')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
        AND despesas.pago = 'S'
ORDER BY despesas.data DESC, despesas.id_despesa DESC
LIMIT 5;"""

last_revenue_query: str = """
SELECT 
    descricao AS 'Descrição',
    receitas.valor AS Valor,
    receitas.data AS Data,
    receitas.categoria AS Categoria,
    receitas.conta AS Conta
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        AND receitas.documento_proprietario_receita = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
WHERE
    receitas.categoria NOT IN ('Pix' , 'TED', 'DOC', 'Ajuste')
    AND receitas.data <= %s
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
        AND receitas.recebido = 'S'
ORDER BY receitas.data DESC , receitas.id_receita DESC
LIMIT 5;"""

total_expense_query: str = """
SELECT 
    CAST(SUM(despesas.valor) AS DECIMAL (10 , 2 ))
FROM
    despesas
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome
        AND despesas.documento_proprietario_despesa = usuarios.cpf
        INNER JOIN
    contas ON despesas.conta = contas.nome_conta
        AND despesas.proprietario_despesa = contas.proprietario_conta
        AND despesas.documento_proprietario_despesa = contas.documento_proprietario_conta
WHERE
    despesas.pago = 'S'
        AND contas.tipo_conta NOT IN('Fundo de Garantia', 'Vale Alimentação')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

total_revenue_query: str = """
SELECT 
    CAST(SUM(receitas.valor) AS DECIMAL (10 , 2 ))
FROM
    receitas
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        AND receitas.documento_proprietario_receita = contas.documento_proprietario_conta
WHERE
    receitas.recebido = 'S'
        AND contas.tipo_conta NOT IN ('Fundo de Garantia' , 'Vale Alimentação')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

accounts_revenue_query: str = """
SELECT 
    CAST(SUM(receitas.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        AND receitas.documento_proprietario_receita = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
WHERE
    receitas.data <= %s
        AND receitas.recebido = 'S'
        AND contas.inativa = 'N'
        AND contas.tipo_conta IN ('Conta Corrente', 'Vale Alimentação', 'Conta Móvel')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
GROUP BY conta
ORDER BY conta ASC;"""

accounts_expenses_query: str = """
SELECT 
    CAST(SUM(despesas.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    despesas
        INNER JOIN
    contas ON despesas.conta = contas.nome_conta
        AND despesas.proprietario_despesa = contas.proprietario_conta
        AND despesas.documento_proprietario_despesa = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome
        AND despesas.documento_proprietario_despesa = usuarios.cpf
WHERE
    despesas.data <= %s
        AND despesas.pago = 'S'
        AND contas.inativa = 'N'
        AND contas.tipo_conta IN ('Conta Corrente', 'Vale Alimentação', 'Conta Móvel')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
GROUP BY conta
ORDER BY conta ASC;
"""

future_accounts_expenses_query: str = """
SELECT 
    CAST(SUM(despesas.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    despesas
        INNER JOIN
    contas ON despesas.conta = contas.nome_conta
        AND despesas.proprietario_despesa = contas.proprietario_conta
        AND despesas.documento_proprietario_despesa = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome
        AND despesas.documento_proprietario_despesa = usuarios.cpf
WHERE
    despesas.data >= %s
        AND despesas.pago = 'N'
        AND contas.inativa = 'N'
        AND contas.tipo_conta IN ('Conta Corrente', 'Vale Alimentação', 'Conta Móvel')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
GROUP BY conta
ORDER BY conta ASC;
"""

future_accounts_revenue_query: str = """
SELECT 
    CAST(SUM(receitas.valor) AS DECIMAL (10 , 2 )) AS Valor
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        AND receitas.documento_proprietario_receita = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
WHERE
    receitas.recebido = 'N'
        AND contas.inativa = 'N'
        AND contas.tipo_conta IN ('Conta Corrente', 'Vale Alimentação', 'Conta Móvel')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
GROUP BY conta
ORDER BY conta ASC;"""

accounts_query: str = """
SELECT DISTINCT
    (contas.nome_conta)
FROM
    contas
        INNER JOIN
    usuarios
WHERE
    contas.inativa = 'N'
        AND contas.tipo_conta IN ('Conta Corrente', 'Vale Alimentação', 'Conta Móvel')
        AND contas.proprietario_conta = usuarios.nome
        AND contas.documento_proprietario_conta = usuarios.cpf
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
ORDER BY contas.nome_conta;"""

max_revenue_query: str = """
SELECT 
    receitas.descricao AS 'Descrição',
    receitas.valor AS 'Valor',
    receitas.data AS 'Data',
    receitas.categoria AS 'Categoria',
    receitas.conta AS 'Conta'
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        AND receitas.documento_proprietario_receita
        AND contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
WHERE
    receitas.categoria <> 'Ajuste'
        AND receitas.data <= %s
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
ORDER BY receitas.valor DESC
LIMIT 5"""

max_expense_query: str = """
SELECT 
    despesas.descricao AS 'Descrição',
    despesas.valor AS 'Valor',
    despesas.data AS 'Data',
    despesas.categoria AS 'Categoria',
    despesas.conta AS 'Conta'
FROM
    despesas
        INNER JOIN
    contas ON despesas.conta = contas.nome_conta
        AND despesas.proprietario_despesa = contas.proprietario_conta
        AND despesas.documento_proprietario_despesa = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome
        AND despesas.documento_proprietario_despesa = usuarios.cpf
WHERE
    despesas.categoria <> 'Ajuste'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
ORDER BY despesas.valor DESC
LIMIT 5;"""

last_expense_id_query: str = """SELECT id_despesa FROM despesas ORDER BY id_despesa DESC LIMIT 1;"""
last_loan_id_query: str = """SELECT id_emprestimo FROM emprestimos ORDER BY id_emprestimo DESC LIMIT 1;"""
last_credit_card_expense_id_query: str = """SELECT id_despesa_cartao FROM despesas_cartao_credito ORDER BY id_despesa_cartao DESC LIMIT 1;"""
last_revenue_id_query: str = """SELECT id_receita FROM receitas ORDER BY id_receita DESC LIMIT 1;"""
last_transfer_id_query: str = """SELECT id_transferencia FROM transferencias ORDER BY id_transferencia DESC LIMIT 1;"""

ticket_revenue_query: str = """
SELECT 
    COALESCE(CAST(SUM(receitas.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        AND receitas.documento_proprietario_receita = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
WHERE
    contas.tipo_conta = 'Vale Alimentação'
AND contas.inativa = 'N'
        AND receitas.recebido = 'S'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

ticket_expense_query: str = """
SELECT 
    COALESCE(CAST(SUM(despesas.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    despesas
        INNER JOIN
    contas ON despesas.conta = contas.nome_conta
        AND despesas.proprietario_despesa = contas.proprietario_conta
        AND despesas.documento_proprietario_despesa = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome
        AND despesas.documento_proprietario_despesa = usuarios.cpf
WHERE
    contas.tipo_conta = 'Vale Alimentação'
AND contas.inativa = 'N'
        AND despesas.pago = 'S'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

loan_expense_query: str = """
SELECT 
    COALESCE(CAST(SUM(emprestimos.valor - emprestimos.valor_pago) AS DECIMAL(10, 2)), 0)
FROM
    emprestimos
INNER JOIN
    usuarios ON emprestimos.credor = usuarios.nome AND emprestimos.documento_credor = usuarios.cpf
WHERE
    emprestimos.pago = 'N'
    AND usuarios.nome = %s
    AND usuarios.cpf = %s;"""

debts_expense_query: str = """
SELECT 
    COALESCE(CAST(SUM(emprestimos.valor - emprestimos.valor_pago) AS DECIMAL (10 , 2 )),
            0)
FROM
    emprestimos
        INNER JOIN
    usuarios ON emprestimos.devedor = usuarios.nome
        AND emprestimos.documento_devedor = usuarios.cpf
WHERE
    emprestimos.pago = 'N'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

fund_revenue_query: str = """
SELECT 
    COALESCE(CAST(SUM(receitas.valor) AS DECIMAL (10 , 2 )), 0)
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        AND receitas.documento_proprietario_receita = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
WHERE
    contas.tipo_conta = 'Fundo de Garantia'
        AND receitas.recebido = 'S'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

fund_expense_query: str = """
SELECT 
    COALESCE(CAST(SUM(despesas.valor) AS DECIMAL (10 , 2 )),
            0)
FROM
    despesas
        INNER JOIN
    contas ON despesas.conta = contas.nome_conta
        AND despesas.proprietario_despesa = contas.proprietario_conta
        AND despesas.documento_proprietario_despesa = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome
        AND despesas.documento_proprietario_despesa = usuarios.cpf
WHERE
    contas.tipo_conta = 'Fundo de Garantia'
        AND despesas.pago = 'S'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

most_categories_expenses_query: str = """
SELECT 
    COALESCE(CAST(SUM(despesas.valor) AS DECIMAL (10 , 2 )),
            0),
    despesas.categoria
FROM
    despesas
        INNER JOIN
    contas ON despesas.conta = contas.nome_conta
        AND despesas.proprietario_despesa = contas.proprietario_conta
        AND despesas.documento_proprietario_despesa = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome
        AND despesas.documento_proprietario_despesa = usuarios.cpf
WHERE
    despesas.categoria NOT IN('Ajuste', 'Fatura Cartão')
        AND contas.tipo_conta IN ('Conta Corrente', 'Vale Alimentação')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
GROUP BY despesas.categoria;"""

most_categories_revenues_query: str = """
SELECT 
    COALESCE(CAST(SUM(receitas.valor) AS DECIMAL (10 , 2 )),
            0),
    receitas.categoria
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        AND receitas.documento_proprietario_receita = contas.documento_proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
WHERE
    receitas.categoria <> 'Ajuste'
        AND contas.tipo_conta IN ('Conta Corrente')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
GROUP BY receitas.categoria;"""

most_credit_card_expenses_query: str = """
SELECT 
    COALESCE(CAST(SUM(despesas_cartao_credito.valor) AS DECIMAL (10 , 2 )),
            0),
    despesas_cartao_credito.categoria
FROM
    despesas_cartao_credito
        INNER JOIN
    cartao_credito ON despesas_cartao_credito.doc_proprietario_cartao = cartao_credito.documento_titular
        AND despesas_cartao_credito.numero_cartao = cartao_credito.numero_cartao
        INNER JOIN
    usuarios ON despesas_cartao_credito.proprietario_despesa_cartao = usuarios.nome
        AND despesas_cartao_credito.doc_proprietario_cartao = usuarios.cpf
WHERE
    despesas_cartao_credito.categoria <> 'Ajuste'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
GROUP BY despesas_cartao_credito.categoria;"""

owner_cards_query = """
SELECT 
    cartao_credito.nome_cartao
FROM
    cartao_credito
        INNER JOIN
    usuarios ON cartao_credito.proprietario_cartao = usuarios.nome
        AND cartao_credito.documento_titular = usuarios.cpf
WHERE
    usuarios.nome = %s
        AND usuarios.cpf = %s;"""

owner_active_cards_query = """
SELECT 
    cartao_credito.nome_cartao
FROM
    cartao_credito
        INNER JOIN
    usuarios ON cartao_credito.proprietario_cartao = usuarios.nome
        AND cartao_credito.documento_titular = usuarios.cpf
WHERE
    usuarios.nome = %s
        AND usuarios.cpf = %s
        AND cartao_credito.inativo = 'N';"""

user_current_accounts_query = """
SELECT 
    contas.nome_conta
FROM
    contas
        INNER JOIN
    usuarios ON contas.proprietario_conta = usuarios.nome
        AND contas.documento_proprietario_conta = usuarios.cpf
WHERE
    contas.tipo_conta IN ('Conta Corrente', 'Vale Alimentação', 'Conta Móvel')
        AND contas.inativa = 'N'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

user_all_current_accounts_query = """
SELECT 
    contas.nome_conta
FROM
    contas
        INNER JOIN
    usuarios ON contas.proprietario_conta = usuarios.nome
        AND contas.documento_proprietario_conta = usuarios.cpf
WHERE
    contas.tipo_conta IN ('Conta Corrente', 'Vale Alimentação', 'Conta Móvel')
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

user_fund_accounts_query = """
SELECT 
    contas.nome_conta
FROM
    contas
        INNER JOIN
    usuarios ON contas.proprietario_conta = usuarios.nome
        AND contas.documento_proprietario_conta = usuarios.cpf
WHERE
    contas.tipo_conta IN ('Fundo de Garantia')
        AND contas.inativa = 'N'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

beneficiaries_query = """
SELECT 
    beneficiados.nome
FROM
    beneficiados
        INNER JOIN
    usuarios ON beneficiados.nome <> usuarios.nome
        AND beneficiados.documento <> usuarios.cpf
WHERE
    usuarios.nome = %s
        AND usuarios.cpf = %s;"""

creditors_query = """SELECT credores.nome FROM credores INNER JOIN usuarios ON credores.nome <> usuarios.nome AND credores.documento <> usuarios.cpf WHERE usuarios.nome = %s AND usuarios.cpf = %s;"""

creditor_doc_name_query = """
SELECT 
    credores.nome,
    credores.documento
FROM
    credores
        INNER JOIN
    usuarios ON credores.nome = usuarios.nome
        AND credores.documento = usuarios.cpf
WHERE
    usuarios.nome = %s
    AND usuarios.cpf = %s;"""

debtors_query: str = """
SELECT 
    emprestimos.devedor
FROM
    emprestimos	
    INNER JOIN beneficiados ON emprestimos.devedor = beneficiados.nome AND emprestimos.documento_devedor = beneficiados.documento
    INNER JOIN credores ON emprestimos.credor = credores.nome AND emprestimos.documento_credor = credores.documento
    INNER JOIN usuarios ON emprestimos.credor = usuarios.nome AND emprestimos.documento_credor = usuarios.cpf
WHERE
    pago = 'N'
    AND usuarios.nome = %s
    AND usuarios.cpf = %s
GROUP BY emprestimos.devedor"""

loan_query: str = """
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
ORDER BY data"""

total_loan_value_query: str = """
SELECT 
    COALESCE(SUM(emprestimos.valor - emprestimos.valor_pago), 0)
FROM
    emprestimos
    INNER JOIN beneficiados ON emprestimos.devedor = beneficiados.nome AND emprestimos.documento_devedor = beneficiados.documento
    INNER JOIN credores ON emprestimos.credor = credores.nome AND emprestimos.documento_credor = credores.documento
    INNER JOIN usuarios ON emprestimos.credor = usuarios.nome AND emprestimos.documento_credor = usuarios.cpf
WHERE
    emprestimos.devedor = %s
    AND usuarios.nome = %s
    AND usuarios.cpf = %s
        AND pago = 'N'"""

not_payed_loans_query = """
SELECT
    emprestimos.id_emprestimo AS 'ID',
    emprestimos.descricao AS 'Descrição',
    emprestimos.valor AS 'Valor',
    emprestimos.valor_pago AS 'Valor Pago',
    emprestimos.valor - emprestimos.valor_pago AS 'Valor a Pagar',
    emprestimos.data AS 'Data',
    emprestimos.categoria AS 'Categoria',
    emprestimos.conta AS 'Conta',
    emprestimos.credor AS 'Credor'
FROM
    emprestimos
    INNER JOIN usuarios ON emprestimos.devedor = usuarios.nome AND emprestimos.documento_devedor = usuarios.cpf
WHERE
    usuarios.nome = %s
    AND usuarios.cpf = %s
    AND pago = 'N';"""

not_received_loans_query = """
SELECT
    emprestimos.id_emprestimo AS 'ID',
    emprestimos.descricao AS 'Descrição',
    emprestimos.valor AS 'Valor',
    emprestimos.valor_pago AS 'Valor Pago',
    emprestimos.valor - emprestimos.valor_pago AS 'Valor a Pagar',
    emprestimos.data AS 'Data',
    emprestimos.categoria AS 'Categoria',
    emprestimos.conta AS 'Conta',
    emprestimos.devedor AS 'Devedor'
FROM
    emprestimos
    INNER JOIN usuarios ON emprestimos.credor = usuarios.nome AND emprestimos.documento_credor = usuarios.cpf
WHERE
    usuarios.nome = %s
    AND usuarios.cpf = %s
    AND pago = 'N';"""

not_received_revenue_query = """SELECT id_receita, descricao, valor, data, horario, categoria, conta
FROM
    receitas
        INNER JOIN
    contas ON contas.nome_conta = receitas.conta
        AND contas.proprietario_conta = receitas.proprietario_receita
        AND contas.documento_proprietario_conta = receitas.documento_proprietario_receita
        INNER JOIN
    usuarios ON receitas.documento_proprietario_receita = usuarios.cpf
        AND receitas.proprietario_receita = usuarios.nome
WHERE
    receitas.recebido = 'N'
        AND receitas.data < '2099-12-31'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

not_received_revenue_ids_query = """SELECT 
    receitas.id_receita
FROM
    receitas
        INNER JOIN
    contas ON contas.nome_conta = receitas.conta
        AND contas.proprietario_conta = receitas.proprietario_receita
        AND contas.documento_proprietario_conta = receitas.documento_proprietario_receita
        INNER JOIN
    usuarios ON receitas.documento_proprietario_receita = usuarios.cpf
        AND receitas.proprietario_receita = usuarios.nome
WHERE
    receitas.recebido = 'N'
        AND receitas.data < '2099-12-31'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

not_payed_expense_query = """SELECT id_despesa, descricao, valor, data, horario, categoria, conta
FROM
    despesas
        INNER JOIN
    contas ON contas.nome_conta = despesas.conta
        AND contas.proprietario_conta = despesas.proprietario_despesa
        AND contas.documento_proprietario_conta = despesas.documento_proprietario_despesa
        INNER JOIN
    usuarios ON despesas.documento_proprietario_despesa = usuarios.cpf
        AND despesas.proprietario_despesa = usuarios.nome
WHERE
    despesas.pago = 'N'
        AND despesas.data < '2099-12-31'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

not_payed_expenses_ids_query = """
SELECT 
    despesas.id_despesa
FROM
    despesas
        INNER JOIN
    contas ON contas.nome_conta = despesas.conta
        AND contas.proprietario_conta = despesas.proprietario_despesa
        AND contas.documento_proprietario_conta = despesas.documento_proprietario_despesa
        INNER JOIN
    usuarios ON despesas.documento_proprietario_despesa = usuarios.cpf
        AND despesas.proprietario_despesa = usuarios.nome
WHERE
    despesas.pago = 'N'
        AND despesas.data < '2099-12-31'
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

expenses_statement_query = """
SELECT 
    despesas.descricao,
    despesas.valor,
    despesas.data,
    despesas.horario,
    despesas.categoria,
    despesas.conta
FROM
    despesas
        INNER JOIN
    contas ON despesas.conta = contas.nome_conta
        AND despesas.proprietario_despesa = contas.proprietario_conta
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome
        AND despesas.documento_proprietario_despesa = usuarios.cpf
WHERE
    despesas.pago = 'S'
        AND despesas.categoria NOT IN('Pix', 'DOC', 'TED')
        AND despesas.data >= %s
        AND despesas.data <= %s
        AND despesas.conta IN %s
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

revenues_statement_query = """
SELECT 
    receitas.descricao,
    receitas.valor,
    receitas.data,
    receitas.horario,
    receitas.categoria,
    receitas.conta
FROM
    receitas
        INNER JOIN
    contas ON receitas.conta = contas.nome_conta
        AND receitas.proprietario_receita = contas.proprietario_conta
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
WHERE
    receitas.recebido = 'S'
        AND receitas.categoria NOT IN('Pix', 'DOC', 'TED')
        AND receitas.data >= %s
        AND receitas.data <= %s
        AND receitas.conta IN %s
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

total_account_revenue_query: str = """
SELECT 
    CAST(SUM(receitas.valor) AS DECIMAL (10 , 2 ))
FROM
    receitas
        INNER JOIN
    usuarios ON receitas.proprietario_receita = usuarios.nome
        AND receitas.documento_proprietario_receita = usuarios.cpf
WHERE
    receitas.recebido = 'S'
        AND receitas.conta = %s
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

total_account_expense_query: str = """
SELECT 
    CAST(SUM(despesas.valor) AS DECIMAL (10, 2))
FROM
    despesas
        INNER JOIN
    usuarios ON despesas.proprietario_despesa = usuarios.nome
        AND despesas.documento_proprietario_despesa = usuarios.cpf
WHERE
    despesas.pago = 'S'
        AND despesas.conta = %s
        AND usuarios.nome = %s
        AND usuarios.cpf = %s;"""

card_invoices_query = """
SELECT
    CONCAT(fechamentos_cartao.mes, " de ", fechamentos_cartao.ano)
FROM
    fechamentos_cartao
        INNER JOIN
    cartao_credito ON fechamentos_cartao.nome_cartao = cartao_credito.nome_cartao
        AND fechamentos_cartao.numero_cartao = cartao_credito.numero_cartao
        INNER JOIN
    usuarios ON usuarios.cpf = fechamentos_cartao.documento_titular
WHERE
    fechamentos_cartao.nome_cartao = %s
        AND usuarios.nome = %s
        AND usuarios.cpf = %s
        AND fechamentos_cartao.fechado = 'N'
ORDER BY fechamentos_cartao.data_comeco_fatura;"""

check_user_query = """SELECT COUNT(id_usuario) FROM usuarios;"""

check_if_user_document_exists_query = """SELECT COUNT(id_usuario) FROM usuarios WHERE cpf = %s;"""
check_if_user_login_exists_query = """SELECT COUNT(id_usuario) FROM usuarios WHERE login = %s;"""
months_query = """SELECT nome_mes FROM meses;"""

creditors_quantity_query = """SELECT COUNT(id_credor) FROM credores INNER JOIN usuarios ON credores.nome = usuarios.nome AND credores.documento = usuarios.cpf WHERE usuarios.login <> %s AND usuarios.senha <> %s;"""

account_image_query = """
    SELECT 
        contas.caminho_arquivo_imagem
    FROM
        contas
            INNER JOIN
        usuarios ON contas.documento_proprietario_conta = usuarios.cpf
            AND contas.proprietario_conta = usuarios.nome
    WHERE
        contas.nome_conta = %s
            AND usuarios.nome = %s
            AND usuarios.cpf = %s;"""

credit_card_expire_date_query = """SELECT cartao_credito.data_validade FROM cartao_credito WHERE cartao_credito.documento_titular = %s AND cartao_credito.nome_cartao = %s AND cartao_credito.proprietario_cartao = %s;"""
