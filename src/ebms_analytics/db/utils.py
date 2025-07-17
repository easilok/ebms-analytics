import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from typing import TypedDict


class DbConfig(TypedDict):
    username: str
    password: str
    host: str
    name: str
    table: str


def create_db_engine(config: DbConfig):
    """Instanciate SQLAlchemy engine based on provided db configuration"""
    return create_engine(
        f"postgresql://{config['username']}:{config['password']}@{config['host']}/{config['name']}"
    )


def insert_on_conflict_nothing(table, conn, keys, data_iter):
    """
    If data being inserted raises a conflict, just skip it and proceed with insertion
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html
    """
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = (
        insert(table.table)
        .values(data)
        .on_conflict_do_nothing(index_elements=["occurrence_id"])
    )
    result = conn.execute(stmt)
    return result.rowcount


def insert_into_database(data: pd.DataFrame, config: DbConfig):
    # Instanciate SQLAlchemy engine
    engine = create_db_engine(config)

    # Write DataFrame to PostgreSQL with options:
    # - If the table does not exist, it will be created automatically.
    # - If it exists, it will append unless you specify if_exists="replace".
    data.to_sql(
        config["table"],
        engine,
        if_exists="append",
        index=False,
        method=insert_on_conflict_nothing,
    )
