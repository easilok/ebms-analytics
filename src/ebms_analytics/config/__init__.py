import os
import tomli
from ebms_analytics.db.utils import DbConfig
from typing import TypedDict, cast

class AppConfig(TypedDict):
   db: DbConfig

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
