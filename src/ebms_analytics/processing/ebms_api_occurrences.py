import os
import requests
import json
import pandas as pd
import time
import sys
from dotenv import load_dotenv
from ebms_analytics.db.utils import insert_into_database
from ebms_analytics.processing.utils import ensure_str, get_obj_path


def get_ebms_api_details():
    load_dotenv()

    warehouse_url = os.getenv('EBMS_WAREHOUSE_URL')
    user = os.getenv('EBMS_API_USER')
    password = os.getenv('EBMS_API_PASSWORD')
    project_id = os.getenv('EBMS_API_PROJECT_ID', 'REBNPORTUGAL')
    es_endpoint = os.getenv('EBMS_API_ES_ENDPOINT', 'es-occurrences')

    # TODO: abort program if missing envs
    if not warehouse_url:
        raise ValueError(f'Missing warehouse api url as EBMS_WAREHOUSE_URL')
    if not user:
        raise ValueError(f'Missing warehouse api username as EBMS_API_USER')
    if not password:
        raise ValueError(f'Missing warehouse api password as EBMS_API_PASSWORD')

    return {
        'endpoint': f'{warehouse_url}/index.php/services/rest/{es_endpoint}/_search/?proj_id={project_id}',
        'username': user,
        'password': password,
    }


def get_ebms_data(payload: dict):
    ebms_api_details = get_ebms_api_details()
    username = ebms_api_details['username']
    password = ebms_api_details['password']

    headers = {
        'User-Agent': 'rebn-client',
        'Content-Type': 'application/json',
        'Authorization': f'USER:{username}:SECRET:{password}',
    }
    response = requests.get(ebms_api_details['endpoint'], json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f'API request failed with status {response.status_code}')

    ebmsData = response.json()
    return ebmsData


COLUMN_MAPPING = {
    'occurrence_key': 'id',
    'location_id': 'location.location_id',
    'location': 'location.name',
    'date': 'event.date_start',
    'recorded_by': 'event.recorded_by',
    'identified_by': 'identification.identified_by',
    'validated_by': 'identification.verifier.name',
    'validation_status': 'identification.verification_status',
    'release_status': 'metadata.release_status',
    'genus': 'taxon.genus',
    'species': 'taxon.species',
    'species_name': 'taxon.accepted_name',
    'family': 'taxon.family',
    'subfamily': 'taxon.subfamily',
    'taxon_rank': 'taxon.taxon_rank',
    'taxon_meaning_id': 'taxon.taxon_meaning_id',
    'life_stage': 'occurrence.life_stage',
    'count': 'occurrence.individual_count',
    'geo': 'location.point',
    'event_start': 'event.date_start',
    'event_end': 'event.date_end',
    'species_authorship': 'taxon.species_authorship',
    'year': 'event.year',
    'month': 'event.month',
    'event_id': 'event.event_id',
    'warehouse_url': 'warehouse',
    'image_filename': 'occurrence.media',
}


def get_ebms_data_from_api(data: list[dict]):
    occurrences = []
    for row in data:
        occurrence = {}
        for column, path in COLUMN_MAPPING.items():
            occurrence[column] = get_obj_path(row['_source'], path)
        if '_id' in row:
            occurrence['occurrence_key'] = row['_id']
        occurrences.append(occurrence)

    return occurrences


def parse_ebms_occurrences(data: list[dict]):
    for occurrence in data:
        occurrence['latitude'] = occurrence['geo'].split(',')[0]
        occurrence['longitude'] = occurrence['geo'].split(',')[1]
        del occurrence['geo']
        occurrence['count'] = occurrence['count'] or 0
        occurrence['taxon_rank'] = ensure_str(occurrence['taxon_rank'], '-')
        occurrence['family'] = ensure_str(occurrence['family'], '-')
        if isinstance(occurrence['species'], str):
            species = occurrence['species'].split(' ')
            if len(species) > 1:
                occurrence['epithet'] = species[1]
        if isinstance(occurrence['image_filename'], list):
            occurrence['image_filename'] = [i['path'] for i in occurrence['image_filename']]
            occurrence['image_paths'] = [
                f'https://{occurrence["warehouse_url"]}/upload/{i}' for i in occurrence['image_filename']
            ]
    return data


def get_ebms_data_page(last_updated_at: str, page: str | None = None):
    payload = {
        'size': 2000,
        'sort': {'metadata.updated_on': {'order': 'asc'}, 'id': {'order': 'asc'}},
        'query': {
            'bool': {
                'must': [
                    {
                        'range': {'event.date_start': {'gte': last_updated_at}},
                        #                 "query_string": {
                        #                     "query": 'location.name:"Belmiro"'
                        #                 }
                    }
                ]
            }
        },
    }

    if isinstance(page, list):
        payload['search_after'] = page
    ebms_data = get_ebms_data(payload)
    if 'hits' not in ebms_data and 'hits' not in ebms_data['hits']:
        raise Exception('eBMS fetched occurrences has invalid structured')

    return ebms_data['hits']['hits'], ebms_data['hits']['total']['value']


def persist_ebms_occurrences(data: pd.DataFrame, db_config: dict[str, any]):
    insert_into_database(data, db_config, db_config['ebms_occurrence_table'])


def import_ebms_occurrences(app_config: dict[str, any]):
    last_updated_at = '1970-01-01'
    total = sys.maxsize
    inserted = 0
    page = None
    result = []

    while inserted < total:
        ebms_data, total = get_ebms_data_page(last_updated_at, page)
        print(
            f'Fetched {inserted + len(ebms_data)} entries out of total {total} '
            f'({round((inserted + len(ebms_data)) / total * 100, 1)} %)'
        )

        if len(ebms_data) == 0:
            # No more results to fetch
            break

        # Parse fetched data
        occurrences = get_ebms_data_from_api(ebms_data)
        parsed_occurrences = parse_ebms_occurrences(occurrences)
        # Extracts information for elastic cache pagination
        # https://www.elastic.co/docs/reference/elasticsearch/rest-apis/paginate-search-results
        page = ebms_data[-1]['sort']
        inserted += len(parsed_occurrences)
        result.extend(parsed_occurrences)
        print(f'Adding {len(parsed_occurrences)} entries for a total {len(result)}')
        persist_ebms_occurrences(pd.DataFrame(parsed_occurrences), app_config['db'])
        time.sleep(2)

    df = pd.DataFrame(result)
    return result
