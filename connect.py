import json
import pathlib
import os
from sqlalchemy import create_engine

def db_connect():

    path = "credentials.json"

    #I'm storing it here, but keeping original functionality
    if not pathlib.Path(path).is_file():
        path = "secrets/credentials.json"

    with open(path) as file:
        credentials = json.load(file)

    MYSQL_IP = credentials["MYSQL_IP"]
    MYSQL_PORT = credentials["MYSQL_PORT"]
    MYSQL_USER = credentials["MYSQL_USER"]
    MYSQL_PASS = credentials["MYSQL_PASS"]
    MYSQL_DB = credentials["MYSQL_DB"]

    GCP_USER = credentials["GCP_USER"]
    GCP_PASS = credentials["GCP_PASS"]
    GCP_DB = credentials["GCP_DB"]
    GCP_CONNECTION_NAME = credentials["GCP_CONNECTION_NAME"]

    if os.environ.get('GAE_INSTANCE'):
        engine = create_engine(
            f"""mysql+pymysql://{GCP_USER}:{GCP_PASS}@/{GCP_DB}?unix_socket=/cloudsql/{GCP_CONNECTION_NAME}""",
            echo = False
        )

    else:
        engine = create_engine(
            f"""mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_IP}:{MYSQL_PORT}/{MYSQL_DB}""",
            echo = False
        )


    return engine