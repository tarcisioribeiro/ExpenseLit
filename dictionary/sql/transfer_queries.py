last_transfer_id_query: str = """
SELECT id FROM transferencias ORDER BY id DESC LIMIT 1;
"""

insert_transfer_query = """
INSERT INTO
    transferencias (
        descricao,
        valor,
        data,
        horario,
        categoria,
        id_conta_origem,
        id_conta_destino,
        id_prop_transferencia,
        doc_prop_transferencia,
        transferido
    )
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
;"""
