import pandas as pd
import click
from ebms_analytics.db.utils import insert_into_database
from ebms_analytics.config import load_config
from ebms_analytics.processing.ebms_occurences import process_ebms_occurrences


@click.command()
@click.option('--config', default="config.toml", type=str, help='Optional configuration file.')
@click.argument('file', required=True)
def app(config:str, file: str):

    app_config = load_config(config)

    data = pd.read_csv(file)
    data = process_ebms_occurrences(data)
    print(data[["latitude", "longitude", "date", "latitude_full", "longitude_full", "verification_status"]])

    insert_into_database(data, app_config["db"])
