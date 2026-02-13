import time
from typing import Optional
import pandas as pd
from ebms_analytics.processing.utils import split_str_series, split_str


COLUMNS_RENAME = {
    'occurrenceID': 'occurrence_key',
    'locationID': 'location_id',
    'country': 'country',
    'stateProvince': 'province',
    'municipality': 'municipality',
    'eventDate': 'date',
    'recordedBy': 'recorded_by',
    'identifiedBy': 'identified_by',
    'family': 'family',
    'genus': 'genus',
    'lifeStage': 'life_stage',
    'individualCount': 'count',
    'decimalLatitude': 'latitude',
    'decimalLongitude': 'longitude',
    'samplingProtocol': 'trap',
    'eventTime': 'event_time',
    'scientificNameAuthorship': 'name_authorship',
    'specificEpithet': 'species',
    # New columns
    'locality': 'locality',
    'countryCode': 'country_code',
    'taxonRank': 'taxon_rank',
    'samplingEffort': 'sampling_effort',
# other
# 'scientificName': 'species',
# 'type': '',
# 'basisOfRecord': '',
# 'institutionCode': '',
# 'collectionCode': '',
# 'datasetName': '',
# 'kingdom': '',
# 'phylum': '',
# 'class': '',
# 'order': '',
# 'verbatimIdentification': '',
# 'occurrenceStatus': '',
# 'coordinatePrecision': '',
# 'georeferenceSources': '',
# 'identificationRemarks': '',
# 'associatedReferences': '',
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
    'locality',
    'country_code',
    'taxon_rank',
    'sampling_effort',
    'name_authorship',
]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df['name'] = (df.genus + ' ' + df.species.fillna('')).astype('str')
    df['name'] = df.name.apply(lambda value: value.strip() if not value == 'nan' else '-')
    df[['event_start_time', 'event_end_time']] = df.event_time.apply(split_str_series(2))
    df['recorded_by'] = list(df.recorded_by.apply(split_str()))
    df['identified_by'] = list(df.identified_by.apply(split_str()))
    df['name_authorship'] = df.name_authorship.apply(lambda val: val.replace('(', '').replace(')', '').strip())
    df = df[df["family"].notna()]

    return df[COLUMNS_TO_KEEP]


def process_gbif_occurrences(data: pd.DataFrame):
    data = data.rename(COLUMNS_RENAME, axis=1)
    # df = df.set_index('occurrenceID', drop=False)
    data = clean_data(data)

    return data
