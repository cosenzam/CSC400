import json
import pathlib
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
    # if os.environ.get ('GAE_INSTANCE'):
    # MYSQL_IP = credentials["MYSQL_IP"]
    # MYSQL_PORT = credentials["MYSQL_PORT"]
    # MYSQL_USER = credentials["MYSQL_USER"]
    # MYSQL_PASS = credentials["MYSQL_PASS"]
    # MYSQL_DB = credentials["MYSQL_DB"]

    engine = create_engine(
        f"""mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_IP}:{MYSQL_PORT}/{MYSQL_DB}""",
        echo = False
    )


    return engine