import os
from dotenv import load_dotenv


load_dotenv()

db_host = os.getenv("DB_HOSTNAME")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_database = os.getenv("DB_NAME")

db_config = {
    "host": db_host,
    "port": db_port,
    "user": db_user,
    "password": db_password,
    "database": db_database,
}

api_key = os.getenv("OPENAI_API_KEY")
