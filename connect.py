import json
from sqlalchemy import create_engine

def db_connect():

    with open("credentials.json") as file:

        credentials = json.load(file)

    MYSQL_IP = credentials["MYSQL_IP"]
    MYSQL_PORT = credentials["MYSQL_PORT"]
    MYSQL_USER = credentials["MYSQL_USER"]
    MYSQL_PASS = credentials["MYSQL_PASS"]
    MYSQL_DB = credentials["MYSQL_DB"]

    engine = create_engine(
        f"""mysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_IP}:{MYSQL_PORT}/{MYSQL_DB}""",
        echo = True
    )

    return engine