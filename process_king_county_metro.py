import pandas as pd
import os


def process_king_country_metro():
    """Process 2022 park & ride data from King County Metro."""

    print('Begin processing King County Metro park & ride data.')

    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/2022/King County/'
    dir_list = os.listdir(file_path)

    # Read xlsx file in folder
    df = pd.read_excel(
        io=file_path + dir_list[0], sheet_name=0, usecols='A:D', skipfooter=1)

    # Generate year averages from monthly/quarterly values
    df = df.groupby(['Name'], as_index=False).agg(total_spaces=('Total Capacity (# of stalls)', 'mean'),
                                                  occupied_spaces=('Mthly - Veh Count', 'mean'))

    # Round decimal values to whole numbers; recalculate utilization
    df = df.round({'occupied_spaces': 0})
    df = df.assign(utilization=df['occupied_spaces']/df['total_spaces'])

    # Create 'agency' column with county name as values
    df.insert(0, 'agency', 'king')

    # add column for ownership_status
    df['owner_status'] = ''
    df['address'] = ''

    # just to make sure all are lowercase
    df.columns = df.columns.str.lower()

    print('All done.')
    return df
