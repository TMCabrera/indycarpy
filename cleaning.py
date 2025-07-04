"""
Cleaning functions for the IndyCar data.
"""

import pandas as pd


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
            "InLap": "in_lap",
            "IsDeleted": "is_deleted",
            "LapsComplete": "laps_complete",
            "LapsDown": "laps_down",
            "LapsLed": "laps_led",
            "LastName": "last_name",
            "PitStops": "pit_stops",
            "PointsEarned": "points_earned",
            "PositionFinish": "position_finish",
            "PositionStart": "position_start",
            "QualLap1": "qual_lap_1",
            "QualLap2": "qual_lap_2",
            "QualLap3": "qual_lap_3",
            "QualLap4": "qual_lap_4",
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

    # We remove the trailing spaces from the status column
    df["status"] = df["status"].str.strip()

    # We drop the columns that are not needed
    columns_to_drop = [
        "speed_avg_formatted",
        "best_speed_formatted",
        "driver_override_id",
    ]
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

    # We drop the columns that are completely empty
    df.dropna(axis=1, how="all", inplace=True)

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
    cols_to_int = [col for col in cols_to_int if col in df.columns]
    if cols_to_int:
        df[cols_to_int] = df[cols_to_int].fillna(0).astype(int)

    # We convert columns to FLOAT type
    df["best_speed"] = df["best_speed"].astype(float)

    return df
