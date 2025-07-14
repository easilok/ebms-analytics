import pandas as pd
from .utils import dataframe_column_renamer

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
    data["family"] = data["family"].fillna('Unknown')

    return data

def process_ebms_occurrences(data: pd.DataFrame):
    data = data.rename(columns=dataframe_column_renamer(list(data.columns)))
    data = clean_data(data)

    return data
