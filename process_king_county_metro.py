import pandas as pd
import os
import pyodbc  # for Elmer connection

def process_king_county_metro(year):
    """Process park & ride data from King County Metro Transit using current project year."""

    print('Begin processing King County Metro Transit park & ride data.')

    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/' + str(year) + '/King County/'
    dir_list = os.listdir(file_path)

    # Read xlsx file in folder
    df = pd.read_excel(
        io=file_path + dir_list[0], sheet_name=0, usecols='A:D'#, skipfooter=1
        )

    # Generate year averages from monthly/quarterly values
    df = df.groupby(['Name'], as_index=False).agg(capacity = ('Total Capacity (# of stalls)', 'mean'),
                                                  occupancy = ('Mthly - Veh Count', 'mean'))

    # Remove (KC) from names
    df['Name'] = df['Name'].str.replace(r'\(KC\)', '', regex=True).str.strip()

    # Fix church names
    df['Name'] = df['Name'].str.replace(r'^(St)', 'St.', regex=True)

    # Round decimal values to whole numbers
    df = df.round({'occupancy': 0})

    # Create 'agency' column with county name as values
    df.insert(0, 'agency', 'King County Metro Transit')

    # Add column for ownership_status
    df['owner_status'] = ''
    df['address'] = ''

    # Ensure all column names are lowercase
    df.columns = df.columns.str.lower()
    
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
        sql="select * from park_and_ride.lot_dim where county_name = 'King'", con=sql_conn)

    # facts table
    master_facts_df = pd.read_sql(
        sql='select * from park_and_ride.park_and_ride_facts', con=sql_conn)

    # join so that lots have capacity numbers for checking against new data
    master_df = pd.merge(master_dim_df, master_facts_df,
                         left_on='lot_dim_id', right_on='lot_dim_id',
                         how="inner")

    # remove lots from Sound Transit
    king_master = master_df[master_df['maintainer_agency'].isin(['King County Metro Transit'])]

    # merge data frames - keep only the current records to determine which ones don't line up with the master list
    king_lots_merge = pd.merge(king_master, df,
                               left_on='lot_name', right_on='name',
                               how="right")

    # remove lots that are in master and do not match in KC Metro data
    maybe_new_lots = king_lots_merge[king_lots_merge['lot_name'].isnull()]
    
    maybe_new_lots.rename({'capacity_y': 'capacity', 'occupancy_y': 'occupancy'}, axis=1, inplace=True)
    
    maybe_new_lots = maybe_new_lots.loc[:, ['agency', 'owner_status', 'name', 'address', 'capacity', 'occupancy']].sort_values(by='name')

    print('All done.')
    return df, maybe_new_lots
