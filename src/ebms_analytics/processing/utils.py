import pandas as pd


def dataframe_column_renamer(columns: list[str]):
    columns_rename = {}
    for c in columns:
        columns_rename[c] = c.replace(' ', '_').lower()

    return columns_rename


def split_str(n: int | None = None):
    def fn(val):
        cols = []
        # Split string by known separators
        if isinstance(val, str):
            if '|' in val:
                cols = val.split('|')
            else:
                cols = val.split('/')

        # Ensure each splitted name entry is trimmed
        cols = [c.strip() for c in cols]

        if n is not None:
            # Ensure at least n splits exist in the result
            for _ in range(n - len(cols)):
                cols.append('')

            # Ensure exactly n splits exist in the result
            return cols[:n]

        return cols

    return fn


def split_str_series(n: int | None = None):
    split = split_str(n)

    def fn(val):
        return pd.Series(split(val))

    return fn


def get_obj_path(data: dict, path: str):
    keys = path.split('.')
    value = data
    for key in keys:
        if not key in value:
            return None
        value = value[key]
    return value



def ensure_str(val: str | None, default=''):
    if not isinstance(val, str) or len(val) == 0:
        return default
    return val
