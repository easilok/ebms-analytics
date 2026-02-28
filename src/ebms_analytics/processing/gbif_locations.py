import pandas as pd
from sqlalchemy import update, Update
from ebms_analytics.db.models import GbifOccurrence


def generate_update_statements(data: pd.DataFrame):
    update_stmts: list[Update] = []

    for index in range(len(data)):
        row = data.iloc[index]
        location_id = row["Location ID"]
        name = row["Nome"]
        update_stmts.append(
            update(GbifOccurrence)
            .where(GbifOccurrence.location_id == int(location_id))
            .values(location = str(name))
        )

    return update_stmts
