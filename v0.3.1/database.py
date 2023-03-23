from ast import Tuple
from types import TracebackType
from typing import List, Dict, Optional, Type, Union
import pyodbc
import os

ALLOWED_DATABASES: List[str] = ['Testes', 'PS_UserData']
DRIVER: str = 'ODBC Driver 17 for SQL Server'
ENCRYPT: str = 'yes'

class Database:
    def __init__(
        self,
        database: str,
        server: str = os.environ['SERVER_DB'],
        username: str = os.environ['USERNAME_DB'],
        password: str = os.environ['PASSWORD_DB'],
        ssl: bool = True
    ) -> None:
        self.driver: str = DRIVER
        self.server: str = server
        self.database: str = database
        self.username: str = username
        self.password: str = password
        self.ssl: bool = ssl
        self.encrypt: str = ENCRYPT

        if self.database not in ALLOWED_DATABASES:
            raise ValueError(f"Banco de dados inválido: {self.database}. Bancos de dados permitidos são {', '.join(ALLOWED_DATABASES)}")

    def __enter__(self) -> 'Database':
        connection_string: str = (
            f"DRIVER={self.driver};"
            f"SERVER={self.server};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"DATABASE={self.database};"
            f"ENCRYPT={self.encrypt};"
        )
        try:
            self.connection: pyodbc.Connection = pyodbc.connect(connection_string)
            return self
        except pyodbc.OperationalError as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise e

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> None:
        self.connection.close()

    def execute_query(self, query: str, params: Optional[Union[Tuple, Dict]] = None) -> List[Dict]:
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return rows
        except pyodbc.Error as e:
            print(f"Erro ao executar a consulta: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

