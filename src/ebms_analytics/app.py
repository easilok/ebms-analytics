import sys
from typing import Optional
import pandas as pd
import click
from ebms_analytics.db.utils import insert_into_database
from ebms_analytics.config import load_config
from ebms_analytics.processing.ebms_occurences import process_ebms_occurrences
from ebms_analytics.processing.occurrences_details import add_session_details
from ebms_analytics.processing.gbif_occurences import import_gbif_occurrences


@click.command()
@click.option('--config', default='config.toml', type=str, help='Optional configuration file.')
@click.option('--weather', is_flag=True, help='Fill weather details on saved sessions.')
@click.option('--gbif', is_flag=True, help='Import GBIF data on database.')
@click.option('--year', type=int, help='Year to import GBIF data.')
@click.option('--month', type=int, help='Month to import GBIF data.')
@click.argument('file', required=False)
def app(
    config: str,
    weather: bool,
    gbif: bool,
    file: str = '',
    year: Optional[int] = None,
    month: Optional[int] = None,
):
    app_config = load_config(config)

    if weather:
        data = add_session_details(app_config['db'])

        insert_into_database(data, app_config['db'], app_config['db']['detail_table'])

    elif gbif:
        if year is None:
            raise click.UsageError('GBIF import require the year of data.')

        data = import_gbif_occurrences(year, month)
        if isinstance(data, pd.DataFrame):
            print(f'Final DataFrame size of {len(data)}')
            insert_into_database(data, app_config['db'], app_config['db']['gbif_table'])
        else:
            print('Could not find any gbif data')

    else:
        if file == '':
            raise click.UsageError('Data to process must be provided.')

        # Allows users to pass CSV as stdin
        if file == '-':
            if sys.stdin.isatty():
                # No pipe or redirect was detected in stdin
                raise click.UsageError('No data provided on stdin')
            try:
                data = pd.read_csv(sys.stdin)
            except pd.errors.EmptyDataError:
                raise click.ClickException('No valid data was detected on stdin.')
        else:
            data = pd.read_csv(file)

        data = process_ebms_occurrences(data)
        print(data[['latitude', 'longitude', 'date', 'latitude_full', 'longitude_full', 'verification_status']])

        insert_into_database(data, app_config['db'], app_config['db']['occurrence_table'])
