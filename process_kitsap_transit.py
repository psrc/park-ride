import pandas as pd
import os
import pyodbc

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
    
    # Remove extra columns
    df.drop(['%'], axis=1, inplace=True)

    # Rename column names
    df.rename({'P&R LOCATION':'name',
               'SPACES':'total_spaces',
               'OCCUPIED SPACES':'occupied_spaces'},
              axis=1, inplace=True)

    # Remove rows using tuple created above
    df = df[~df['name'].isin(del_rows)]

    # Replace asteriks in names
    df['name'] = df['name'].str.replace(r'\*+', '', regex=True).str.strip()

    # Copy values for Clearwater Casino and Poulsbo Junction; delete extra rows
    df.iloc[3, 1:4] = df.iloc[4, 1:4]
    df.iloc[7, 1:4] = df.iloc[8, 1:4]
    df = df[~df['name'].str.contains(r'=\d+\)', regex=True)]

    # Round decimal values to whole numbers
    df = df.round({'occupied_spaces':0})

    # Create 'agency' column with agency name as values
    df.insert(0, 'agency', 'Kitsap Transit')
    
    print('All done.')
    return df

def clean_names_kitsap_transit():
    """Clean names of 2022 park & ride lots from Kitsap Transit to match master data."""

    print('Begin renaming process for aligning Kitsap Transit park & ride data.')

    # view data from Kitsap Transit
    kitsap_data = process_kitsap_transit()

    print('Connecting to Elmer to pull master data park and ride lots')
    
    # connect to master data
    conn_string = (
        r'Driver=SQL Server;'
        r'Server=AWS-Prod-SQL\Sockeye;'
        r'Database=Elmer;'
        r'Trusted_Connection=yes;')

    sql_conn = pyodbc.connect(conn_string)

    # dim table
    master_dim_df = pd.read_sql(
        sql="select * from park_and_ride.lot_dim where county_name = 'Kitsap'", con=sql_conn)

    # facts table
    master_facts_df = pd.read_sql(
        sql='select * from park_and_ride.park_and_ride_facts', con=sql_conn)
    
    # join so that lots have capacity numbers for checking against new data
    kitsap_master = pd.merge(master_dim_df, master_facts_df,
                             left_on='lot_dim_id', right_on='lot_dim_id',
                             how="inner")
    
    # merge data frames - keep only the 2022 records to determine which ones don't line up with the master list
    kitsap_lots_merge22 = pd.merge(kitsap_master, kitsap_data,
                                   left_on='lot_name', right_on='name',
                                   how="right")

    # remove lots that are in master and do not match in Kitsap data - this step is for checking lots
    maybe_new_lots = kitsap_lots_merge22[kitsap_lots_merge22['lot_name'].isnull()]
    
    print('Renaming lots with inconsistent names')
    # rename 12 'new' lots - those in the new data set that don't match the master list
    kitsap_data_renamed = kitsap_data.replace({'name': {'1st United Methodist Church': 'First United Methodist Church',
                                                        'Annapolis Park & Ride': 'Annapolis P&R',
                                                        'Burly Bible Church': 'Burley Bible Church',
                                                        'Crossroads Church': 'Crossroads Neighborhood Church',
                                                        'Day Road & SR 305': 'Day Rd & SR 305',
                                                        'Gateway Center': 'Gateway',
                                                        'George\'s Corners': 'George\'s Corner',
                                                        'Harper Free Evangelical Church': 'Harper Evangelical Free Church',
                                                        'McWilliams Park & Ride': 'McWilliams P&R',
                                                        'Mullenix and Highway 16': 'Mullenix Road P&R',
                                                        'North Base Park & Ride': 'North Base',
                                                        'Olalla Valley Fire Station': 'Olalla Valley'}
                                               })

    return kitsap_data_renamed
