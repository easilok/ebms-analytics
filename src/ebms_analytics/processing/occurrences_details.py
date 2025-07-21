import datetime as dt
from typing import cast
import pandas as pd
from meteostat import Hourly, Point
from sqlalchemy import desc, exists, select
from ebms_analytics.db.utils import create_db_engine
from ebms_analytics.db.models import Occurrence, SessionDetail


def _get_monitor_sessions(config):
    """Gets all moth monitoring sessions IDs, dates and coordinates that still don't have weather details.
    It only gets sessions from specific stations."""
    engine = create_db_engine(config)

    stations = [
        305262,  # Parque Biológico
        305242,  # Moinho do Belmiro
        308157, # Lymantria
    ]

    subq = select(SessionDetail.fk_sample_id).where(SessionDetail.fk_sample_id == Occurrence.sample_id)

    stmt = (
        select(
            Occurrence.sample_id,
            Occurrence.date,
            Occurrence.longitude,
            Occurrence.latitude,
        )
        .filter(Occurrence.location_id.in_(stations))
        .filter(~exists(subq))
        .group_by(
            Occurrence.sample_id,
            Occurrence.date,
            Occurrence.longitude,
            Occurrence.latitude,
        )
        .order_by(desc(Occurrence.sample_id))
    )

    df = pd.DataFrame()

    with engine.connect() as eng:
        df = pd.read_sql(stmt, eng)
        df['date'] = pd.to_datetime(df.date)

    return df


def _get_session_weather(session: pd.Series):
    """Fetches weather data of a specific `session`.
    Weather data is retrieved and resampled from 20:00 to 8:00 next day."""
    # Set time period
    session_date = cast(dt.datetime, session.date)
    start = session_date.replace(hour=20, minute=0)
    end = session_date.replace(hour=8, minute=0) + dt.timedelta(days=1)

    # Get hourly data
    point = Point(session.latitude, session.longitude)
    weather = Hourly(point, start, end).fetch()

    session_weather = pd.Series()
    session_weather['fk_sample_id'] = session.sample_id
    session_weather['ambient_start_at'] = weather.index.min()
    session_weather['ambient_start_at'] = weather.index.min()
    session_weather['ambient_end_at'] = weather.index.max()
    session_weather['temp_max'] = weather.temp.max()
    session_weather['temp_min'] = weather.temp.min()
    session_weather['temp_mean'] = weather.temp.mean()
    session_weather['precipitation_max'] = weather.prcp.max()
    session_weather['precipitation_min'] = weather.prcp.min()
    session_weather['precipitation_mean'] = weather.prcp.mean()
    session_weather['rel_hum_max'] = weather.rhum.max()
    session_weather['rel_hum_min'] = weather.rhum.min()
    session_weather['rel_hum_mean'] = weather.rhum.mean()
    session_weather['wind_speed_max'] = weather.wspd.max()
    session_weather['wind_speed_min'] = weather.wspd.min()
    session_weather['wind_speed_mean'] = weather.wspd.mean()
    session_weather['wind_dir_mean'] = weather.wdir.mean()
    session_weather['weather_condition_code'] = weather.coco.mode().iloc[0]

    return session_weather


def add_session_details(config):
    """Fetches weather data for all the supported stations and builds a new pandas DataFrame with those contents."""
    df_occurrences = _get_monitor_sessions(config)
    df = pd.DataFrame()
    for i in range(len(df_occurrences)):
        weather = _get_session_weather(df_occurrences.iloc[i])
        df = pd.concat([df, weather.to_frame().T], ignore_index=True)
        print(f'Fetched {round((i + 1) / len(df_occurrences) * 100, 1)}%.')

    return df
