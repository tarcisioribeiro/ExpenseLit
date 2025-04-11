#!/usr/bin/env bash
host="localhost"
port="$1"
shift
cmd="$@"

echo "Aguardando MySQL em $host:$port..."
while ! timeout 1 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; do
  sleep 2
done

echo "MySQL está pronto! Iniciando a aplicação..."
exec $cmd
