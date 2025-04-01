FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip mysql-server netcat \
    && apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN service mysql start && \
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'orrARDrdr27!'; FLUSH PRIVILEGES;" && \
    mysql -uroot -p'orrARDrdr27!' < reference/database/implantation_financas.sql

EXPOSE 8551 20306

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD service mysql start && /wait-for-it.sh 3306 -- streamlit run main.py --server.port=8551

