import geopandas as gpd
import mgrs
import os
import pandas as pd
import requests
import sys
import time
from dotenv import load_dotenv
from sqlalchemy import desc, select
from ebms_analytics.db.utils import create_db_engine
from ebms_analytics.db.utils import insert_into_database
from ebms_analytics.db.models import EbmsOccurrence
from ebms_analytics.processing.utils import ensure_str, get_obj_path, trim_str


def _get_last_registered_occurrence(config, default: str) -> str:
    "Gets the most recent updated record"
    engine = create_db_engine(config)

    stmt = (
        select(
            EbmsOccurrence.updated_at,
        )
        .order_by(desc(EbmsOccurrence.updated_at))
        .limit(1)
    )

    with engine.begin() as conn:
        last_occurrence = conn.execute(stmt).first()
        if last_occurrence is None:
            return default

        return last_occurrence.updated_at.isoformat()


def _get_ebms_api_details():
    load_dotenv()

    warehouse_url = os.getenv('EBMS_WAREHOUSE_URL')
    user = os.getenv('EBMS_API_USER')
    password = os.getenv('EBMS_API_PASSWORD')
    project_id = os.getenv('EBMS_API_PROJECT_ID', 'REBNPORTUGAL')
    es_endpoint = os.getenv('EBMS_API_ES_ENDPOINT', 'es-occurrences')

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


def _get_ebms_data(payload: dict):
    ebms_api_details = _get_ebms_api_details()
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
    'occurrence_id': 'id',
    'location_id': 'location.location_id',
    'location': 'location.name',
    'event_date': 'event.date_start',
    'recorded_by': 'event.recorded_by',
    'identified_by': 'identification.identified_by',
    'validated_by': 'identification.verifier.name',
    'identification_verification_status': 'identification.verification_status',
    'release_status': 'metadata.release_status',
    'genus': 'taxon.genus',
    'species': 'taxon.species',
    'species_name': 'taxon.accepted_name',
    'family': 'taxon.family',
    'subfamily': 'taxon.subfamily',
    'taxon_rank': 'taxon.taxon_rank',
    'taxon_meaning_id': 'taxon.taxon_meaning_id',
    'life_stage': 'occurrence.life_stage',
    'individual_count': 'occurrence.individual_count',
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

# Columns: ['id', 'dtmnfr', 'freguesia', 'tipo_area_administrativa', 'municipio', 'distrito_ilha', 'nuts3_cod', 'nuts3', 'nuts2', 'nuts1', 'area_ha', 'perimetro_km', 'geometry']
# [{'id': 1, 'dtmnfr': '160938', 'freguesia': 'Vila de Punhe', 'tipo_area_administrativa': 'Área Principal', 'municipio': 'Viana do Castelo', 'distrito_ilha': 'Viana do Castelo', 'nuts3_cod': '111', 'nuts3': 'Alto Minho', 'nuts2': 'Norte', 'nuts1': 'Continente', 'area_ha': 602.67, 'perimetro_km': 12},
# {'id': 2, 'dtmnfr': '160935', 'freguesia': 'Vila Franca', 'tipo_area_administrativa': 'Área Principal', 'municipio': 'Viana do Castelo', 'distrito_ilha': 'Viana do Castelo', 'nuts3_cod': '111', 'nuts3': 'Alto Minho', 'nuts2': 'Norte', 'nuts1': 'Continente', 'area_ha': 714.6, 'perimetro_km': 11}]
TERRITORY_COLUMN_MAPPING = {
    'locality': 'freguesia',
    'municipality': 'municipio',
    'county': 'distrito_ilha',
    'state_province': 'Province',
    'region': 'nuts2',
}


def _get_ebms_data_from_api(data: list[dict]):
    occurrences = []
    for row in data:
        occurrence = {}
        for column, path in COLUMN_MAPPING.items():
            occurrence[column] = get_obj_path(row['_source'], path)
        if '_id' in row:
            occurrence['occurrence_id'] = row['_id']
        occurrences.append(occurrence)

    return occurrences


def parse_ebms_occurrences(data: list[dict]):
    m = mgrs.MGRS()
    for occurrence in data:
        occurrence['decimal_latitude'] = float(occurrence['geo'].split(',')[0])
        occurrence['decimal_longitude'] = float(occurrence['geo'].split(',')[1])
        del occurrence['geo']
        occurrence['mgrs'] = m.toMGRS(occurrence['decimal_latitude'], occurrence['decimal_longitude'])
        occurrence['individual_count'] = occurrence['individual_count'] or 0
        occurrence['taxon_rank'] = ensure_str(occurrence['taxon_rank'], '-')
        occurrence['family'] = ensure_str(occurrence['family'], '-')
        occurrence['species_authorship'] = trim_str(
            ensure_str(occurrence['species_authorship']).replace('(', '').replace(')', '')
        )
        occurrence['scientific_name_authorship'] = trim_str(f'({occurrence["species_authorship"]})')
        occurrence['scientific_name'] = f'{trim_str(occurrence["species"])} {occurrence["scientific_name_authorship"]}'
        occurrence['location'] = trim_str(occurrence['location'])
        occurrence['recorded_by'] = trim_str(occurrence['recorded_by'])
        occurrence['identified_by'] = trim_str(occurrence['identified_by'])
        occurrence['validated_by'] = trim_str(occurrence['validated_by'])
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
    ebms_data = _get_ebms_data(payload)
    if 'hits' not in ebms_data and 'hits' not in ebms_data['hits']:
        raise Exception('eBMS fetched occurrences has invalid structured')

    return ebms_data['hits']['hits'], ebms_data['hits']['total']['value']


def attach_location_territory(
    occurrences: pd.DataFrame,
    geopackage_path='./resources/Continente_CAOP2025.gpkg',
    province_shape_path='./resources/Províncias_Corley2015.shp',
) -> pd.DataFrame:

    if occurrences.empty:
        return occurrences

    if len(geopackage_path) == 0:
        return occurrences

    occurrences_columns = list(occurrences.columns)
    # Portugal CAOP geopackage layer structure
    #                           name geometry_type
    # 0  cont_areas_administrativas       Polygon
    # 1              cont_distritos  MultiPolygon
    # 2             cont_freguesias  MultiPolygon
    # 3             cont_municipios  MultiPolygon
    # 4                  cont_nuts1  MultiPolygon
    # 5                  cont_nuts2  MultiPolygon
    # 6                  cont_nuts3  MultiPolygon
    # 7                 cont_trocos    LineString
    # 8                layer_styles          None
    # 9             inf_fonte_troco          None

    occurrences = gpd.GeoDataFrame(
        occurrences.copy(),
        geometry=gpd.points_from_xy(
            occurrences['decimal_longitude'],
            occurrences['decimal_latitude'],
        ),
        crs='EPSG:4326',
    )

    territory = gpd.read_file(
        geopackage_path,
        layer='cont_areas_administrativas',
    )

    occurrences = occurrences.to_crs(territory.crs)

    occurrences = gpd.sjoin(
        occurrences,
        territory,
        how='left',
        predicate='within',
    ).drop(columns='index_right', errors='ignore')

    provinces = gpd.read_file(province_shape_path)

    # Match coordinate systems
    provinces = provinces.to_crs(occurrences.crs)

    # Add province attributes to each occurrence
    occurrences = gpd.sjoin(
        occurrences,
        provinces,
        how='left',
        predicate='within',
    ).drop(columns='index_right', errors='ignore')

    occurrences = occurrences.rename(columns={val: key for key, val in TERRITORY_COLUMN_MAPPING.items()})

    columns_to_keep = occurrences_columns + list(TERRITORY_COLUMN_MAPPING.keys())
    occurrences = occurrences.reindex(columns=[c for c in columns_to_keep if c in occurrences.columns])
    occurrences['country'] = 'Portugal'

    return occurrences


def persist_ebms_occurrences(data: pd.DataFrame, db_config: dict[str, any]):
    insert_into_database(data, db_config, db_config['ebms_occurrence_table'])


def import_ebms_occurrences(db_config: dict[str, any]):
    last_updated_at = '1970-01-01'
    total = sys.maxsize
    inserted = 0
    page = None
    result = []

    last_updated_at = _get_last_registered_occurrence(db_config, '1970-01-01')

    print(f'Starting importing from {last_updated_at}')

    while inserted < total:
        ebms_data, total = get_ebms_data_page(last_updated_at, page)

        if total == 0:
            print('No new data to insert')
            break

        print(
            f'Fetched {inserted + len(ebms_data)} entries out of total {total} '
            f'({round((inserted + len(ebms_data)) / total * 100, 1)} %)'
        )

        if len(ebms_data) == 0:
            # No more results to fetch
            break

        # Parse fetched data
        occurrences = _get_ebms_data_from_api(ebms_data)
        parsed_occurrences = parse_ebms_occurrences(occurrences)
        # Extracts information for elastic cache pagination
        # https://www.elastic.co/docs/reference/elasticsearch/rest-apis/paginate-search-results
        page = ebms_data[-1]['sort']
        inserted += len(parsed_occurrences)
        result.extend(parsed_occurrences)
        print(f'Adding {len(parsed_occurrences)} entries for a total {len(result)}')
        df = pd.DataFrame(parsed_occurrences)
        df = attach_location_territory(df)
        persist_ebms_occurrences(df, db_config)
        time.sleep(2)

    return result
