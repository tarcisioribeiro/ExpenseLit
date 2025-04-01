import os
from dotenv import load_dotenv


load_dotenv()

db_host = 'localhost'
db_port = 3306
db_user = 'root'
db_password =  '123'
db_database = 'financas'

db_config = {
    "host": db_host,
    "port": db_port,
    "user": db_user,
    "password": db_password,
    "database": db_database,
}