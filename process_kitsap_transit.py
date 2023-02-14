import pandas as pd
import os

def process_kitsap_transit():
    """Process 2022 park & ride data from Kitsap Transit."""
    
    print('Begin processing Kitsap Transit park & ride data.')
    
    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/2022/Kitsap Transit/'
    dir_list = os.listdir(file_path)

    # Create tuple of rows to remove from the data
    del_rows = ('NORTH', 'BAINBRIDGE', 'CENTRAL', 'SOUTH')

    # Read xlsx file in folder
    df = pd.read_excel(io=file_path + dir_list[0], sheet_name=0, usecols='A:D', skipfooter=1)

    # Rename column names
    df.rename({'P&R LOCATION':'name',
               'SPACES':'total_spaces',
               'OCCUPIED SPACES':'occupied_spaces',
               '%':'utilization'},
              axis=1, inplace=True)

    # Remove rows using tuple created above
    df = df[~df['name'].isin(del_rows)]

    # Replace asteriks in names
    df['name'] = df['name'].str.replace(r'\*+', '', regex=True).str.strip()

    # Copy values for Clearwater Casino and Poulsbo Junction; delete extra rows
    df.iloc[3, 1:4] = df.iloc[4, 1:4]
    df.iloc[7, 1:4] = df.iloc[8, 1:4]
    df = df[~df['name'].str.contains(r'=\d+\)', regex=True)]

    # Round decimal values to whole numbers; recalculate utilization
    df = df.round({'occupied_spaces':0})
    df = df.assign(utilization=df['occupied_spaces']/df['total_spaces'])

    # Create 'agency' column with agency name as values
    df.insert(0, 'agency', 'Kitsap Transit')
    
    print('All done.')
    return df
