#!/bin/bash
set -e

echo ">> Aguardando o MySQL iniciar..."

until mysqladmin ping -h "$DB_HOSTNAME" --silent; do
  sleep 1
done

echo ">> Criando usuário de aplicação '${DB_USER}' no banco '${DB_NAME}'..."

mysql -h "$DB_HOSTNAME" -uroot -p"${MYSQL_ROOT_PASSWORD}" <<-EOSQL
    CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';
    GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'%';
    FLUSH PRIVILEGES;
EOSQL

echo ">> Script de inicialização concluído!"

DEFAULT_SRC="library/images/default.png"
DEFAULT_DEST="library/images/accounts/default.png"

# Verifica se a imagem já existe, senão copia
if [ ! -f "$DEFAULT_DEST" ]; then
  echo ">> default.png não encontrado em accounts/. Copiando..."
  cp "$DEFAULT_SRC" "$DEFAULT_DEST"
else
  echo ">> default.png já está presente em accounts/"
fi

# Executa o comando original
exec "$@"
