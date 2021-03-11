from urllib.parse import quote_plus

from sqlalchemy import create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import MetaData


class Alch:
    def __init__(self, server, login, password, database, schema):
        # https://docs.sqlalchemy.org/en/13/dialects/mssql.html#pass-through-exact-pyodbc-string
        params = quote_plus(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};DATABASE={database};UID={login};PWD={password}'
        )
        engine = create_engine('mssql+pyodbc:///?odbc_connect=' + params)

        self.Base = declarative_base()
        self.metadata = MetaData(bind=engine, schema=schema)
        self.session = sessionmaker(bind=engine)()
        self.Table = Table
