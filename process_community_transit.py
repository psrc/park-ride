import pandas as pd
import os


def process_community_transit():
    """Process 2022 park & ride data from Community Transit."""

    print('Begin processing Community Transit park & ride data.')

    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/2022/Community Transit/'
    dir_list = os.listdir(file_path)

    # Read xlsx file in folder
    df = pd.read_excel(
        io=file_path + dir_list[0], sheet_name=0,  # usecols='A:D',
        header=2)

    # Remove extra columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed: 0')]

    # Remove leading spaces for column names
    df.columns = df.columns.str.strip()

    # Rename column names
    df.rename({'Facility_Type': 'owner_status',
               'Facility': 'name',
               'Facility_Address': 'address',
               'AVG_Stall_Count': 'total_spaces',
               'AVG_Parked_Vehicles': 'occupied_spaces',
               'AVG_Utilization': 'utilization'},
              axis=1, inplace=True)

    # Change ownership_status options
    df['owner_status'].replace({'MAJOR': 'permanent',
                                'MINOR': 'permanent',
                                'LEASE': 'lease'},
                               inplace=True)

    # Convert object type to float
    # df['total_spaces'] = df['total_spaces'].astype(float)
    # df['occupied_spaces'] = df['occupied_spaces'].astype(float)

    # Create 'agency' column with county name as values
    df.insert(0, 'agency', 'community transit')

    # Ensure all column names are lowercase
    df.columns = df.columns.str.lower()

    print('All done.')
    return df
