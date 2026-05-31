from sqlalchemy import create_engine, text
import os

from dotenv import load_dotenv
load_dotenv()


LOCAL_DB_CONNECTION_STRING = os.getenv("LOCAL_DB_CONNECTION_STRING")
engine = create_engine(LOCAL_DB_CONNECTION_STRING, future=True)

def query(sql, params=None):
    with engine.raw_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or {})
        rows = cursor.fetchall()
        engine.dispose()
        return rows, cursor



        
#-----------------------------------
#     Below is for cloud connection. Keep for now!
#-----------------------------------
# from google.cloud.sql.connector import Connector
# import sqlalchemy
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")
# DB_USER = os.getenv("DB_USER")
# INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

# connector = Connector()

# def getconn():
#     conn = connector.connect(
#         INSTANCE_CONNECTION_NAME,
#         "pg8000",
#         user=DB_USER,
#         password=DB_PASSWORD,
#         db=DB_NAME
#     )
#     return conn

# engine = sqlalchemy.create_engine(
#     "postgresql+pg8000://",
#     creator=getconn,
# )




