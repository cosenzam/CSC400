import json
import pathlib
from sqlalchemy import create_engine

def db_connect():

    path = "secrets/credentials_gcp.json"

    with open(path) as file:
        credentials = json.load(file)

    USER = credentials["USER"]
    PASSWORD = credentials["PASSWORD"]
    PUBLIC_IP = credentials["PUBLIC_IP"]
    PROJECT_ID = credentials["PROJECT_ID"]
    DB_NAME = credentials["DB_NAME"]
    INSTANCE_NAME = credentials["INSTANCE_NAME"]

    engine = create_engine(
        f"""
            mysql+pymysql://{USER}:{PASSWORD}@{PUBLIC_IP}/{DB_NAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"""
    )

    return engine