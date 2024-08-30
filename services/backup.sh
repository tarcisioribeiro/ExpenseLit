cd data/database/

sleep 1

rm *.7z

sleep 1

mysqldump -u{user} -p{password} --port=20306 --host=localhost --databases financas > backup_financas.sql

sleep 1

7z a backup_financas.7z backup_financas.sql

rm *.sql
