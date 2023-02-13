import pandas as pd
import os


def process_pierce_transit():
    """Process 2022 park & ride data from Pierce Transit."""

    print('Begin processing Pierce Transit park & ride data.')

    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/2022/Pierce Transit/'
    dir_list = os.listdir(file_path)

    # Read xlsx file in folder
    df = pd.read_excel(
        io=file_path + dir_list[0], sheet_name=0,  header=1)

    # Remove bottom total row
    df = df.iloc[:-1]

    # Remove leading spaces for column names
    df.columns = df.columns.str.strip()

    # Rename column names
    df.rename({'Name and Address': 'name',
               'of': 'total_spaces'},
              axis=1, inplace=True)

    # Remove unnecessary header row
    df = df.iloc[1:]

    # Remove quarterly occupancy/utilization values
    df.drop(df.filter(regex='Avg|%').columns, axis=1, inplace=True)

    # create column with average occupancy
    df["occupied_spaces"] = df.loc[:, [
        col for col in df if col.startswith('Unnamed')]].mean(axis=1)

    # remove all month columns
    df.drop(df.filter(regex='Unnamed').columns, axis=1, inplace=True)

    # convert object type to float
    df['total_spaces'] = df['total_spaces'].astype(float)
    df['occupied_spaces'] = df['occupied_spaces'].astype(float)

    # calculate utilization rate
    df['utilization'] = df['occupied_spaces']/df['total_spaces']

    # add column for ownership_status
    df['owner_status'] = ''
    df['address'] = ''

    # Create 'agency' column with county name as values
    df.insert(0, 'agency', 'pierce transit')

    # Ensure all column names are lowercase
    df.columns = df.columns.str.lower()

    print('All done.')
    return df
