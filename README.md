# IndyCarPy

IndyCarPy is a Python package designed to scrape IndyCar session data from
the official IndyCar website. It provides functionalities to retrieve
information about races, practices, qualifications, and warm-up sessions,
as well as the records associated with these sessions.

## Features

- **Session Data Retrieval**: Fetch data about IndyCar sessions including
  races, practices, qualifications, and warm-ups.
- **Data Cleaning and Preparation**: Clean and prepare the retrieved data
  for further analysis or storage.
- **Export to CSV**: Option to export the data to CSV format for easy
  integration with other tools or databases.

## Installation

You can install IndyCarPy using pip:

```bash
pip install indycarpy
```

Make sure you have the required dependencies installed: `pandas`,
`requests`, `tqdm`, and `numpy`.

## Usage

```bash
import indycarpy

# Retrieve race session data between specific years
indycarpy.get_sessions_records(from_year=1996, to_year=2024, session_type="R", data_format="df")

# Clean session records data
cleaned_data = indycarpy.clean_sessions_records(sessions_df)
```

## Data Files

This package includes a `data/race_track.csv` file containing information
about the track names for each event, which is utilized during data
retrieval.

## Contributing

Contributions to IndyCarPy are welcome! If you encounter any issues or have
suggestions for improvements, feel free to open an issue or submit a pull
request on GitHub.

## License

IndyCarPy is licensed under the GNU General Public License v3.0. See the
LICENSE file for more details.
