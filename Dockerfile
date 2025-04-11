FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.10 python3-pip mysql-server netcat \
    curl wget nano \
    && apt-get clean

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN service mysql start && \
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123'; FLUSH PRIVILEGES;" && \
    mysql -uroot -p'123' < reference/database/implantation_financas.sql

EXPOSE 8551 20306

COPY reference/services/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["sh", "-c", "service mysql start && /wait-for-it.sh 3306 -- streamlit run main.py --server.port=8551 --server.address=0.0.0.0"]
