import sqlite3
from google.cloud.sql.connector import Connector, IPTypes
import pg8000
import sqlalchemy
import psycopg2

# connect_with_connector initializes a connection pool for a
# Cloud SQL instance of Postgres using the Cloud SQL Python Connector.
def connect_with_connector(db_user, db_pass, instance_connection_name, db_name):

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector()

    def getconn() -> pg8000.dbapi.Connection:
        conn: pg8000.dbapi.Connection = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn

    db = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn
    )
    conn = db.connect()
    return conn
    
def connect_with_conn_string(user, pw, host, db_name, use_psycopg2=False):
    conn_string = f"postgresql+pg8000://{user}:{pw}@{host}/{db_name}"
    if use_psycopg2:
        conn_string = f"postgresql+psycopg2://{user}:{pw}@{host}/{db_name}"
    db = sqlalchemy.create_engine(conn_string)
    conn = db.connect()
    return conn
    
def connect_with_sqlite(sqlite_file):
    db = sqlalchemy.create_engine(f'sqlite:///{sqlite_file}?check_same_thread=False')
    conn = db.connect()
    return conn