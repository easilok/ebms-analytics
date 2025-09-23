import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from typing import TypedDict


class DbConfig(TypedDict):
    username: str
    password: str
    host: str
    name: str
    occurrence_table: str
    detail_table: str
    gbif_table: str


conflict_index_keys = {
    'ocurrence': ['occurrence_id'],
    'gbif_occurrence': ['occurrence_key'],
    # Code should avoid inserting an existing sample_id already
    # 'session_detail': ['fk_sample_id'],
}


def create_db_engine(config: DbConfig):
    """Instanciate SQLAlchemy engine based on provided db configuration"""
    return create_engine(f'postgresql://{config["username"]}:{config["password"]}@{config["host"]}/{config["name"]}')


def insert_on_conflict_nothing(table, conn, keys, data_iter):
    """
    If data being inserted raises a conflict, just skip it and proceed with insertion
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html
    """
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = insert(table.table).values(data)
    table_name = str(table.table)
    if table_name in conflict_index_keys:
        stmt = stmt.on_conflict_do_nothing(index_elements=conflict_index_keys[table_name])
    result = conn.execute(stmt)
    return result.rowcount


def insert_into_database(data: pd.DataFrame, config: DbConfig, table: str = 'occurrence'):
    """Inserts all data from a pandas DataFrame into a database.
    Database connection is set from `config` and the destination `table`."""
    # Instanciate SQLAlchemy engine
    engine = create_db_engine(config)

    # Write DataFrame to PostgreSQL with options:
    # - If the table does not exist, it will be created automatically.
    # - If it exists, it will append unless you specify if_exists="replace".
    data.to_sql(
        table,
        engine,
        if_exists='append',
        index=False,
        method=insert_on_conflict_nothing,
    )
