"""
This is the main file for the IndyCar Scraper package.
"""

# Standard library imports
import json
from datetime import datetime
import time
import pkg_resources

# Related third-party imports
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

# Local application/library specific imports
from . import helper

# We define the URLS for scraping the data
SEASON_DROP_DOWN = "https://www.indycar.com/Services/IndyStats.svc/SeasonDropDown?id=b856a4f1-e85c-4fac-8c36-fd58d962227a"
EVENTS_SESSION_URL = (
    "https://www.indycar.com/Services/IndyStats.svc/EventsSessionDetails?id={}"
)

# We define the session object
s = requests.Session()


def get_sessions(from_year: int = 1996, to_year: int = 2024) -> pd.DataFrame:
    """
    This function retrieves the list of sessions from the IndyCar API
    between the specified years.

    Parameters
    ----------
    from_year : int
        The start year.
    to_year : int
        The end year.

    Returns
    -------
    pd.DataFrame
        The DataFrame containing the sessions. It has the following columns:
        - Year
        - EventID
        - EventName
        - SessionID
        - SessionName ("Race", "Practice", "Qualifications", "Warmup"...)
    """
    response = s.get(SEASON_DROP_DOWN, timeout=5)
    if response.status_code != 200:
        raise Exception("Failed to retrieve sessions.")
    r = response.content.decode("utf-8")
    seasons_json = json.loads(r)

    events_list = []

    for i in seasons_json:
        year = i["Year"]
        int_year = int(year)
        if (int_year >= from_year) and (int_year <= to_year):
            for j in i["Events"]:
                event_id = j["EventID"]
                event_name = j["EventName"]

                for y in j["Sessions"]:

                    session_dict = {
                        "Year": year,
                        "EventID": event_id,
                        "EventName": event_name,
                        "SessionID": y["EventsSessionID"],
                        "SessionName": y["SessionName"],
                    }

                    events_list.append(session_dict)

    df_all = pd.DataFrame(events_list)

    return df_all


def get_sessions_records(
    from_year: int = 1996,
    to_year: int = 2024,
    session_type: str = "R",
    data_format: str = "df",
) -> pd.DataFrame or None:
    """
    This function retrieves the list of sessions records from the IndyCar API.

    Parameters
    ----------
    from_year : int
        The start year.
    to_year : int
        The end year.
    session_type : str
        The session type to filter: "R", "P", "Q", "W" or "All".
    data_format : str
        The output format: "df" or "csv".

    Returns
    -------
    pd.DataFrame or None
        The DataFrame containing the sessions records. It has the following columns:
        - BestLapTime
        - BestSpeed
        - BestSpeedFormatted
        - CarNumber
        - Difference
        - DriverName
        - DriverOverrideID
        - DriversID
        - ElapsedTime
        - EventsEntrylistID
        - EventsSessionsDetailsID
        - EventsSessionsID
        - FirstName
        - Gap
        - IsDeleted
        - LapsComplete
        - LapsDown
        - LapsLed
        - LastName
        - PitStops
        - PointsEarned
        - PositionFinish
        - PositionStart
        - SpeedAvg
        - SpeedAvgFormatted
        - Status
        - TimesLed
        - EventName
        - TrackName
        - EventDate
        - EventType
        - SessionType
        - TrackType
        - EventID
        - Season
    """
    sessions = get_sessions(from_year, to_year)

    if session_type == "R":
        sessions = sessions[sessions["SessionName"].str.contains("Race")]
    elif session_type == "P":
        sessions = sessions[sessions["SessionName"].str.contains("Practice")]
    elif session_type == "Q":
        sessions = sessions[sessions["SessionName"].str.contains("Qualif")]
    elif session_type == "W":
        sessions = sessions[sessions["SessionName"].str.contains("Warm")]

    sessions_ids = sessions["SessionID"].to_list()

    track_data_path = pkg_resources.resource_filename(
        "indycarpy", "data/race_track.csv"
    )

    track_df = pd.read_csv(track_data_path, sep=";")

    race_sessions_list = []

    for event_id in tqdm(sessions_ids):
        time.sleep(0.2)
        response = s.get(EVENTS_SESSION_URL.format(event_id))
        races_sessions = json.loads(response.content.decode("utf-8"))

        event_name = races_sessions["EventName"]

        # If the event name is in the track_df, we get the track name
        # and assign it to the track_name variable. Otherwise, it's none
        track_name = (
            track_df.loc[track_df["EventName"] == event_name, "TrackName"].values[0]
            if event_name in track_df["EventName"].values
            else None
        )

        for session in races_sessions["records"]:
            session["EventName"] = event_name
            session["TrackName"] = track_name
            session["EventDate"] = races_sessions["SessionDate"]
            session["EventType"] = races_sessions["SessionName"]
            session["SessionType"] = races_sessions["SessionType"]
            session["TrackType"] = races_sessions["TrackType"]
            session["EventID"] = event_id
            session["Season"] = datetime.strptime(
                races_sessions["SessionDate"], "%m/%d/%Y"
            ).year

            race_sessions_list.append(session)

    df_sessions = pd.DataFrame(race_sessions_list)

    if data_format == "df":
        return df_sessions
    elif data_format == "csv":
        if from_year == to_year:
            filename = f"sessions_{from_year}"
        else:
            filename = f"sessions_{from_year}_{to_year}"
        helper.df_to_csv(df_sessions, filename)
        return None
    else:
        raise ValueError("Output type must be 'csv' or 'df'.")


def get_unique_drivers(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function retrieves the unique drivers from
    """
    unique_drivers = df.groupby(["driver_name", "drivers_id"])

    return unique_drivers


def clean_sessions_records(df: pd.DataFrame, session_type: str = "R") -> pd.DataFrame:
    """
    This function cleans the data.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the sessions records.
    session_type : str
        The session type to filter: "R", "P", "Q", "W" or "All".

    Returns
    -------
    pd.DataFrame
        The cleaned DataFrame.
    """
    # We start by renaming the columns
    df = df.rename(
        {
            "BestLapTime": "best_lap_time",
            "BestSpeed": "best_speed",
            "BestSpeedFormatted": "best_speed_formatted",
            "CarNumber": "car_number",
            "Difference": "difference",
            "DriverName": "driver_name",
            "DriverOverrideID": "driver_override_id",
            "DriversID": "drivers_id",
            "ElapsedTime": "elapsed_time",
            "EventsEntrylistID": "events_entrylist_id",
            "EventsSessionsDetailsID": "events_sessions_details_id",
            "EventsSessionsID": "events_sessions_id",
            "FirstName": "first_name",
            "Gap": "gap",
            "IsDeleted": "is_deleted",
            "LapsComplete": "laps_complete",
            "LapsDown": "laps_down",
            "LapsLed": "laps_led",
            "LastName": "last_name",
            "PitStops": "pit_stops",
            "PointsEarned": "points_earned",
            "PositionFinish": "position_finish",
            "PositionStart": "position_start",
            "SpeedAvg": "speed_avg",
            "SpeedAvgFormatted": "speed_avg_formatted",
            "Status": "status",
            "TimesLed": "times_led",
            "EventName": "event_name",
            "TrackName": "track_name",
            "EventDate": "event_date",
            "EventType": "event_type",
            "SessionType": "session_type",
            "TrackType": "track_type",
            "EventID": "event_id",
            "Season": "season",
        },
        axis=1,
    )

    # We filter the dataframe by session type
    if session_type.lower() != "all":
        df = df[df["session_type"] == session_type]

    # We drop the columns that are completely empty
    df.dropna(axis=1, how="all", inplace=True)

    # We replace the NaN values with None (for Supabase compatibility)

    # We drop the columns that are not needed
    df.drop(
        columns=[
            "speed_avg_formatted",
            "best_speed_formatted",
            "driver_override_id",
        ],
        inplace=True,
    )

    # We drop the is_deleted column if it only has one unique value
    if df["is_deleted"].nunique() == 1:
        df.drop(columns=["is_deleted"], inplace=True)

    # We convert columns to INT type
    cols_to_int = [
        "laps_led",
        "times_led",
        "position_start",
        "position_finish",
        "pit_stops",
    ]
    df[cols_to_int] = df[cols_to_int].fillna(0).astype(int)

    if session_type.lower() == "r":
        # We create a new column to store the change in position between the grid and the finish
        df["position_change"] = df["position_start"] - df["position_finish"]

    # We convert columns to FLOAT type
    df["best_speed"] = df["best_speed"].astype(float)

    return df
