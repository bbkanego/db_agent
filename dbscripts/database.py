import ast
import os
from typing import List

import dotenv
import psycopg2
import pickle
import psycopg2.pool
from dotenv import load_dotenv
from psycopg2.extensions import connection, cursor
from sqlalchemy import engine

_connection: connection = None

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def get_seerworks_db_connection() -> connection:
    return get_db_connection(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

def get_engine():
    # Database connection details
    sql_rule = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    #connection = get_db_connection(db_host=DB_HOST, db_name=DB_NAME, db_user=DB_USER, db_password=DB_PASSWORD)
    engine_obj = engine.create_engine(url=sql_rule)
    return engine_obj

def get_db_connection(db_host, db_name, db_user, db_password) -> connection:
    global _connection
    try:
        if _connection is None:
            simple_connection_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=3,
                                                                        host=db_host, dbname=db_name,
                                                                        user=db_user, password=db_password)
            if (simple_connection_pool):
                _connection = simple_connection_pool.getconn()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while connecting to PostgreSQL", error)
    return _connection


def insert_chunked_data(type=str, chunk_data=[]):
    if chunk_data is None or len(chunk_data) == 0:
        return

    tuples = []
    for chunk in chunk_data:
        # this is basically creating tuples like [('Bhushan', 'key1'), ('James', 'key2')]
        tuples.append((str(chunk.to_dict()), type, psycopg2.Binary(pickle.dumps(chunk))))
    # print(tuples)
    records_list_template = ','.join(['%s'] * len(tuples))
    # print(records_list_template)
    insert_query = "INSERT INTO chunked_data (chunk, chunk_info, chunk_bytes) VALUES {}".format(records_list_template)
    # print(insert_query)
    # print(tuples)
    cursor = get_seerworks_db_connection().cursor()
    cursor.execute(insert_query, tuples)
    cursor.connection.commit()


def read_chunks_of_type(type: str):
    cursor = get_seerworks_db_connection().cursor()
    cursor.execute("select * from chunked_data where chunk_info = %s", (type,))
    # print((pickle.loads(cursor.fetchone()[4])).to_dict())
    return cursor.fetchall()


def convert_literal_str_to_dict(literal_str: str):
    return ast.literal_eval(literal_str)

# print((read_chunks_of_type(type='composite')))
