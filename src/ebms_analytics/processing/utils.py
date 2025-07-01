from typing import List

def dataframe_column_renamer(columns: List[str]):
    columns_rename = {}
    for c in columns:
        columns_rename[c] = c.replace(" ", "_").lower()

    return columns_rename


