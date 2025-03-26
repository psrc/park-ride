import pandas as pd
import os
import pyodbc  # for Elmer connection

def process_community_transit(year):
    """Process park & ride data from Community Transit using current project year."""

    print('Begin processing Community Transit park & ride data.')

    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/' + str(year) + '/Community Transit/'
    dir_list = os.listdir(file_path)

    # Read xlsx file in folder
    df = pd.read_excel(
        io=file_path + dir_list[0], sheet_name=0,
        skipfooter=2)

    # Remove extra columns
    df.drop(['AVG Utilization', 'Owner', 'Maintenance'], axis=1, inplace=True)

    # Remove leading spaces for column names
    df.columns = df.columns.str.strip()

    # Rename column names
    df.rename({'Facility Type': 'owner_status',
               'Facility': 'name',
               'Facility Address': 'address',
               'AVG Stall Count': 'capacity',
               'AVG Parked Vehicles': 'occupancy'},
              axis=1, inplace=True)

    # Change ownership_status options
    df['owner_status'].replace({'Major Park & Ride (>= 250 Parking Stalls)': 'permanent',
                                'Minor Park & Ride (<250 Stalls)': 'permanent',
                                'Leased Lot': 'leased'},
                               inplace=True)
    
    # Create notes column
    df['notes'] = None

    # Create 'agency' column with county name as values
    df.insert(0, 'agency', 'Community Transit')

    # Ensure all column names are lowercase
    df.columns = df.columns.str.lower()
    
    # remove Lynnwood and Mountlake Terrace lots - used in Sound Transit data instead
    df = df.drop(df[(df.name == 'Lynnwood') |
                    (df.name == 'Mountlake Terrace')].index)
    
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
        sql='select * from park_and_ride.lot_dim', con=sql_conn)

    # facts table
    master_facts_df = pd.read_sql(
        sql='select * from park_and_ride.park_and_ride_facts', con=sql_conn)

    # join so that lots have capacity numbers for checking against new data
    master_df = pd.merge(master_dim_df, master_facts_df,
                         left_on='lot_dim_id', right_on='lot_dim_id',
                         how="inner")

    # filter lots in Community County from master df
    community_master = master_df[master_df['maintainer_agency'].isin(['Community Transit'])]

    # merge data frames - keep only the current records to determine which ones don't line up with the master list
    community_lots_merge = pd.merge(community_master, df,
                                    left_on='lot_name', right_on='name',
                                    how="right")

    # remove lots that are in master and do not match in Community Transit data
    maybe_new_lots = community_lots_merge[community_lots_merge['lot_name'].isnull()]
    
    maybe_new_lots.rename({'capacity_y': 'capacity', 'occupancy_y': 'occupancy'}, axis=1, inplace=True)
    
    maybe_new_lots = maybe_new_lots.loc[:, ['agency', 'owner_status', 'name', 'address', 'capacity', 'occupancy']].sort_values(by='name')

    print('All done.')
    return df, maybe_new_lots
