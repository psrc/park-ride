import pandas as pd
import os
import pyodbc

def process_kitsap_transit(year):
    """Process park & ride data from Kitsap Transit using current project year."""
    
    print('Begin processing Kitsap Transit park & ride data.')
    
    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/' + str(year) + '/Kitsap Transit/'
    dir_list = os.listdir(file_path)

    # Create tuple of rows to remove from the data
    #del_rows = ('NORTH', 'BAINBRIDGE', 'CENTRAL', 'SOUTH')

    # Read xlsx file in folder
    df = pd.read_excel(io=file_path + dir_list[0], sheet_name=1, usecols='B:D', skipfooter=1)
    
    # Remove extra columns
    #df.drop(['%'], axis=1, inplace=True)

    # Rename column names
    df.rename({'LOCATION':'name',
               'SPACES':'capacity',
               'YTD AVERAGE':'occupancy'},
              axis=1, inplace=True)

    # Remove rows using tuple created above
    #df = df[~df['name'].isin(del_rows)]

    # Replace asteriks in names
    df['name'] = df['name'].str.replace(r'\*+', '', regex=True).str.strip()

    # Copy values for Clearwater Casino and Poulsbo Junction; delete extra rows
    #df.iloc[3, 1:4] = df.iloc[4, 1:4]
    #df.iloc[7, 1:4] = df.iloc[8, 1:4]
    #df = df[~df['name'].str.contains(r'=\d+\)', regex=True)]
    
    # Remove info in parentheses for Clearwater Casino and Poulsbo Junction
    df['name'] = df['name'].str.replace(r'\(.+\)$', '', regex=True).str.strip()

    # Round decimal values to whole numbers
    df = df.round({'occupancy':0})
    
    # Create notes column
    df['notes'] = None

    # Create 'agency' column with agency name as values
    df.insert(0, 'agency', 'Kitsap Transit')
    
    print('Connecting to Elmer to pull master data park and ride lots')
    
    # connect to master data
    conn_string = (
        r'Driver=SQL Server;'
        r'Server=SQLserver;'
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
    
    # merge data frames - keep only the current records to determine which ones don't line up with the master list
    kitsap_lots_merge = pd.merge(kitsap_master, df,
                                 left_on='lot_name', right_on='name',
                                 how="right")

    # remove lots that are in master and do not match in Kitsap Transit data
    maybe_new_lots = kitsap_lots_merge[kitsap_lots_merge['lot_name'].isnull()]
    
    maybe_new_lots.rename({'capacity_y': 'capacity', 'occupancy_y': 'occupancy'}, axis=1, inplace=True)
    
    maybe_new_lots = maybe_new_lots.loc[:, ['agency', 'name', 'capacity', 'occupancy']].sort_values(by='name')
    
    print('All done.')
    return df, maybe_new_lots
