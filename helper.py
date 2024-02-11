"""
Helper functions.
"""

import os
import pandas as pd


def df_to_csv(df: pd.DataFrame, filename: str) -> None:
    """
    This function takes a Pandas DataFrame and writes it to a CSV file
    inside the output directory.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to work with.
    filename : str
        The filename to write to.
    """
    # We establish the output directory, and create it if it doesn't exist.
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # We write the DataFrame to a CSV file.
    filename = os.path.join(output_dir, filename + ".csv")
    df.to_csv(filename, index=False)
