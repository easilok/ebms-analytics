import os
import pandas as pd
import click
import tomli
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from typing import List, Optional, TypedDict, cast

class DbConfig(TypedDict):
   username: str
   password: str
   host: str
   name: str
   table: str

class AppConfig(TypedDict):
   db: DbConfig

def dataframe_column_renamer(columns: List[str]):
    columns_rename = {}
    for c in columns:
        columns_rename[c] = c.replace(" ", "_").lower()

    return columns_rename

def coordinate_converter(coordinate: str):
    if coordinate.endswith('S') or coordinate.endswith('W'):
        coordinate = f"-{coordinate}"

    return float(coordinate[:-1])

def clean_data(data: pd.DataFrame):
    data.date = pd.to_datetime(data.date, format="%d/%m/%Y")
    data["latitude_full"] = data["latitude"]
    data["longitude_full"] = data["longitude"]
    data["latitude"] = data["latitude"].apply(coordinate_converter)
    data["longitude"] = data["longitude"].apply(coordinate_converter)
    data["verification_status"] = data["verification_status"] == "V"
    data["count_outside"] = data["count_outside"].fillna(0)
    data["count_inside"] = data["count_inside"].fillna(0)

    return data

def insert_on_conflict_nothing(table, conn, keys, data_iter):
    """
    If data being inserted raises a conflict, just skip it and proceed with insertion
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html
    """
    data = [dict(zip(keys, row)) for row in data_iter]
    stmt = insert(table.table).values(data).on_conflict_do_nothing(index_elements=["occurrence_id"])
    result = conn.execute(stmt)
    return result.rowcount

def insert_into_database(data: pd.DataFrame, config: DbConfig):
    # Instanciate SQLAlchemy engine
    engine = create_engine(f"postgresql://{config['username']}:{config['password']}@{config['host']}/{config['name']}")

    # Write DataFrame to PostgreSQL with options:
    # - If the table does not exist, it will be created automatically.
    # - If it exists, it will append unless you specify if_exists="replace".
    data.to_sql(config['table'], engine, if_exists="append", index=False, method=insert_on_conflict_nothing)

def validate_config(config):
    if not "username" in config["db"] or config["db"]["username"] is None:
        return False, "Missing 'username' in database config."

    if not "password" in config["db"] or config["db"]["password"] is None:
        return False, "Missing 'password' in database config."

    if not "host" in config["db"] or config["db"]["host"] is None:
        return False, "Missing 'host' in database config."

    if not "name" in config["db"] or config["db"]["name"] is None:
        return False, "Missing 'name' in database config."

    if not "table" in config["db"] or config["db"]["table"] is None:
        return False, "Missing 'table' in database config."

    return True, ""

def load_config(filepath: str):
    config = {}
    if os.path.isfile(filepath):
        with open(filepath, "rb") as f:
            config = tomli.load(f)
    else:
        print(f"Could not find configuration file at '{filepath}'")

    if not "db" in config or config["db"] is None:
        config["db"] = {}

    config["db"]["username"] = os.getenv("DATABASE_USERNAME", config["db"].get("username"))
    config["db"]["password"] = os.getenv("DATABASE_PASSWORD", config["db"].get("password"))
    config["db"]["host"] = os.getenv("DATABASE_HOST", config["db"].get("host", "localhost:5432"))
    config["db"]["name"] = os.getenv("DATABASE_NAME", config["db"].get("name", "ebms-analytics"))
    config["db"]["table"] = os.getenv("DATABASE_TABLE", config["db"].get("table", "ocurrence"))

    valid, error = validate_config(config)
    if not valid:
        raise ValueError(f"Invalid Config. {error}")

    return cast(AppConfig, config)

@click.command()
@click.option('--config', default="config.toml", type=str, help='Optional configuration file.')
@click.argument('file', required=True)
def app(config:str, file: str):

    app_config = load_config(config)

    data = pd.read_csv(file)
    data = data.rename(columns=dataframe_column_renamer(list(data.columns)))
    data = clean_data(data)
    print(data[["latitude", "longitude", "date", "latitude_full", "longitude_full", "verification_status"]])

    insert_into_database(data, app_config["db"])

if __name__ == "__main__":
    app()
