"""
Analysis module for IndyCar data
"""

import pandas as pd
import numpy as np
from scipy.stats import hmean


def get_unique_drivers(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function retrieves the unique drivers from a results DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the sessions records.

    Returns
    -------
    pd.DataFrame
        The DataFrame containing the unique drivers.
    """
    unique_drivers = df.groupby(["driver_name", "drivers_id"])

    return unique_drivers


def add_running_counts(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function adds a new column to the dataframe with the count of running cars for each event_id.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the sessions records.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the new column 'running_cars'.
    """

    # Filter dataframe where Status is 'Running'
    running_df = df[df["status"] == "Running"]

    # Count occurrences for each event_id
    running_counts = running_df["event_id"].value_counts()

    # Add new column 'running_cars' to original dataframe
    df["running_cars"] = df["event_id"].map(running_counts)

    # Replace NaN values with 0
    df["running_cars"].fillna(0, inplace=True)
    df["running_cars"] = df["running_cars"].astype(int)

    return df


def add_finished_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function adds a new column to the dataframe with the ranking of the
    driver among those who finished the race with a status of "Running".

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the sessions records.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the new column 'position_finish_only'.
    """
    df = add_running_counts(df)
    # Initialize the new column with np.nan
    df["position_finish_only"] = np.nan

    # Find the indices of rows where status is "Running"
    running_indices = df[df["status"] == "Running"].index

    # Rank the position_finish within each event_id group for rows where status is "Running"
    df.loc[running_indices, "position_finish_only"] = (
        df.loc[running_indices]
        .groupby("event_id")["position_finish"]
        .rank(method="min")
        .astype("Int64")
    )

    return df


def add_finish_percentile(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function adds a new column to the dataframe with the percentile of the
    finishing position for each event_id.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the sessions records.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the new column 'finish_percentile'.
    """

    df = add_finished_ranking(df)

    df["finish_percentile"] = np.nan
    df.loc[df["status"] == "Running", "finish_percentile"] = (
        (df["running_cars"] - df["position_finish_only"]) / (df["running_cars"] - 1)
    ) * 100

    # We round the finish percentile to 2 decimal places
    df["finish_percentile"] = df["finish_percentile"].round(2)

    # We drop the finish_position_only column
    df.drop(columns="position_finish_only", inplace=True)

    return df


def calculate_cpi(average_finish_percentile, finish_rate):
    """
    This function calculates the Consistency Performance Index (CPI) for each driver.

    Parameters
    ----------
    average_finish_percentile : pd.Series
        The average finish percentile for each driver.
    finish_rate : pd.Series
        The finish rate for each driver.

    Returns
    -------
    pd.Series
        The Consistency Performance Index (CPI) for each driver.
    """
    return hmean([average_finish_percentile, finish_rate], axis=0).round(2)


def get_cpi_df(
    df: pd.DataFrame, by_season: bool = False, drop: int = 0
) -> pd.DataFrame:
    """
    This function creates a DataFrame with the Consistency Performance Index (CPI)

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the sessions records.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the finish percentile for each driver.
    """

    df = add_finish_percentile(df)

    if by_season:
        group = ["season", "driver_name"]
    else:
        group = ["driver_name"]

    grouped = df.groupby(group).agg(
        driver_name=pd.NamedAgg(column="driver_name", aggfunc="first"),
        races_completed=pd.NamedAgg(column="driver_name", aggfunc="count"),
        average_starting_position=pd.NamedAgg(column="position_start", aggfunc="mean"),
        average_finish_position=pd.NamedAgg(column="position_finish", aggfunc="mean"),
        finish_percentile_index=pd.NamedAgg(column="finish_percentile", aggfunc="mean"),
        finish_rate=pd.NamedAgg(
            column="status", aggfunc=lambda x: (x == "Running").sum() / len(x) * 100
        ),
        adj_finish_rate=pd.NamedAgg(
            column="status",
            aggfunc=lambda x: (
                (x == "Running").sum() / (len(x) - (x == "Mechanical").sum()) * 100
                if (len(x) - (x == "Mechanical").sum()) != 0
                else 0
            ),
        ),
        points_earned=pd.NamedAgg(column="points_earned", aggfunc="sum"),
        points_per_race=pd.NamedAgg(
            column="points_earned", aggfunc=lambda x: x.sum() / len(x)
        ),
    )

    # Calculate points_per_race
    grouped["points_per_race"] = (
        grouped["points_earned"] / grouped["races_completed"]
    ).round(1)

    # Calculate consistency_performance_index
    grouped["race_performance_index"] = calculate_cpi(
        grouped["finish_percentile_index"], grouped["adj_finish_rate"]
    )

    # Round the other columns
    grouped = grouped.round(
        {
            "average_starting_position": 1,
            "average_finish_position": 1,
            "finish_percentile_index": 2,
            "finish_rate": 2,
            "adj_finish_rate": 2,
        }
    )

    if by_season:
        grouped["season"] = grouped.index.get_level_values("season")
        grouped = grouped[
            [
                "driver_name",
                "season",
                "races_completed",
                "average_starting_position",
                "average_finish_position",
                "finish_percentile_index",
                "finish_rate",
                "adj_finish_rate",
                "points_earned",
                "points_per_race",
                "race_performance_index",
            ]
        ]

    if drop > 0:
        grouped = grouped[grouped["races_completed"] >= drop]

    # Sort the DataFrame by CPI
    summary_df = grouped.sort_values(by="race_performance_index", ascending=False)

    return summary_df
