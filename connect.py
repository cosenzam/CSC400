import json
import pathlib
from sqlalchemy import create_engine
from google.cloud.sql.connector import Connector



def db_connect():

    path = "secrets/credentials_gcp.json"

    with open(path) as file:
        credentials = json.load(file)

    USER = credentials["USER"]
    PASSWORD = credentials["PASSWORD"]
    PUBLIC_IP = credentials["PUBLIC_IP"]
    PROJECT_ID = credentials["PROJECT_ID"]
    DB_NAME = credentials["DB_NAME"]
    REGION = credentials["REGION"]
    INSTANCE_NAME = credentials["INSTANCE_NAME"]

    INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"

    connector = Connector()
    def get_conn():
        conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pymysql",
        user=USER,
        password=PASSWORD,
        db=DB_NAME
        )
        return conn

    engine = create_engine(
        f"mysql+pymysql://",
        creator=get_conn
    )

    return engine