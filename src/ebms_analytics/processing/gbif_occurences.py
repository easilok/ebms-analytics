import time
from http import HTTPStatus
from typing import Optional
import pandas as pd
from pygbif import occurrences
from requests.exceptions import HTTPError


EBMS_DATASET_KEY = '59161187-c444-48cd-9efc-c286e10d034e'

COLUMNS_RENAME = {
    'key': 'occurrence_key',
    'locationID': 'location_id',
    'country': 'country',
    'stateProvince': 'province',
    'county': 'county',
    'municipality': 'municipality',
    'eventDate': 'date',
    'recordedBy': 'recorded_by',
    'identifiedBy': 'identified_by',
    'species': 'species',
    'genus': 'genus',
    'family': 'family',
    'lifeStage': 'life_stage',
    'individualCount': 'count',
    'decimalLatitude': 'latitude',
    'decimalLongitude': 'longitude',
    'samplingProtocol': 'trap',
    'eventTime': 'event_time',
    'scientificNameAuthorship': 'name_authorship',
}

COLUMNS_TO_KEEP = [
    'occurrence_key',
    'location_id',
    'country',
    'province',
    'county',
    'municipality',
    'date',
    'recorded_by',
    'identified_by',
    'species',
    'genus',
    'name',
    'family',
    'life_stage',
    'count',
    'latitude',
    'longitude',
    'trap',
    'event_time',
    'event_start_time',
    'event_end_time',
    'name_authorship',
]


def split_str(n: Optional[int] = None):
    def fn(val):
        cols = []
        # Split string by known separators
        if isinstance(val, str):
            if '|' in val:
                cols = val.split('|')
            else:
                cols = val.split('/')

        if n is not None:
            # Ensure at least n splits exist in the result
            for _ in range(n - len(cols)):
                cols.append('')

            # Ensure exactly n splits exist in the result
            return cols[:n]

        return cols

    return fn


def split_str_series(n: Optional[int] = None):
    split = split_str(n)

    def fn(val):
        return pd.Series(split(val))

    return fn


def parse_gbif_request(data: list) -> pd.DataFrame:
    df = pd.DataFrame(data)
    if df.empty:
        return df

    df = df.set_index('key', drop=False)
    df = df.rename(COLUMNS_RENAME, axis=1)
    df['name'] = df.species.fillna(df.genus)
    df[['event_start_time', 'event_end_time']] = df.event_time.apply(split_str_series(2))
    df['recorded_by'] = list(df.recorded_by.apply(split_str()))
    df['identified_by'] = list(df.identified_by.apply(split_str()))

    return df[COLUMNS_TO_KEEP]


def fetch_gbif_occurences_batch(dataset_key: str, year: int, month: int) -> list:
    # Fetch first batch
    total = 301
    offset = 0
    limit = 300
    occurences = []
    requests = 1

    while offset < total:
        data = occurrences.search(
            datasetKey=dataset_key,
            year=year,
            month=month,
            offset=offset,
            limit=limit,
        )

        total = data['count']
        print(f'Request {requests} completed: {offset}/{total}')

        occurences.extend(data['results'])
        offset += limit
        requests += 1

        if requests % 10 == 0:
            print('Sleeping for 5 seconds to ease rate limiter.')
            time.sleep(5)

    return occurences


def import_gbif_occurrences(year: int, month: Optional[int] = None):
    # Fetch only selected month or all year if no selection provided
    start_month = month or 1
    end_month = month or 12
    result = None
    for month in range(start_month, end_month + 1):
        print(f'Fetching year {year} and month {month}')
        occurrences = []
        try:
            occurrences = fetch_gbif_occurences_batch(
                EBMS_DATASET_KEY,
                year,
                month,
            )
        except HTTPError as exc:
            code = exc.response.status_code
            if code == HTTPStatus.TOO_MANY_REQUESTS:
                print('Rate limiter hit. Wait 30 seconds and retry.')
                time.sleep(30)
                occurrences = fetch_gbif_occurences_batch(
                    EBMS_DATASET_KEY,
                    year,
                    month,
                )

        if result is None:
            result = []
        result.extend(occurrences)
        if month < end_month:
            print('Sleeping for 5 seconds between months to ease rate limiter.')
            time.sleep(5)

    if isinstance(result, list):
        print(f'Resulting DataFrame size of {len(result)}')
        return parse_gbif_request(result)

    return None
