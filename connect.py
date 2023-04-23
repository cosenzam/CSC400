import json
import pathlib
import os
from sqlalchemy import create_engine
import logging

def db_connect():

    path = "credentials.json"

    #I'm storing it here, but keeping original functionality


    # if not pathlib.Path(path).is_file():
    #     path = "secrets/credentials.json"
    # with open(path) as file:
    #     credentials = json.load(file)

    # MYSQL_IP = credentials["MYSQL_IP"]
    # MYSQL_PORT = credentials["MYSQL_PORT"]
    # MYSQL_USER = credentials["MYSQL_USER"]
    # MYSQL_PASS = credentials["MYSQL_PASS"]
    # MYSQL_DB = credentials["MYSQL_DB"]

    # engine = create_engine(
    #     f"""mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_IP}:{MYSQL_PORT}/{MYSQL_DB}""",
    #     echo = False
    # )


    # from google.cloud import secretmanager
    # client = secretmanager.SecretManagerServiceClient()


    # project_id ="cryptic-saga-384600"
    # secret_id = "CLOUD_SQL_CREDENTIALS_SECRET"
    # version_id="latest"
    # name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    # response = client.access_secret_version(request={"name": name})

    credentials = json.loads(os.environ["CLOUD_SQL_CREDENTIALS_SECRET"])
    logging.info(credentials)

    GCP_USER = credentials["GCP_USER"]
    GCP_PASS = credentials["GCP_PASS"]
    GCP_DB = credentials["GCP_DB"]
    GCP_CONNECTION_NAME = credentials["GCP_CONNECTION_NAME"]

    engine = create_engine(
        f"""mysql+pymysql://{GCP_USER}:{GCP_PASS}@/{GCP_DB}?unix_socket=/cloudsql/{GCP_CONNECTION_NAME}""",
        echo = False
    )

    return engine