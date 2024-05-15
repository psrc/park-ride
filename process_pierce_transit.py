import pandas as pd
import os
import pyodbc  # for Elmer connection

def process_pierce_transit(year):
    """Process park & ride data from Pierce Transit using current project year."""

    print('Begin processing Pierce Transit park & ride data.')

    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/' + str(year) + '/Pierce Transit/'
    dir_list = os.listdir(file_path)

    # Read xlsx file in folder
    df = pd.read_excel(
        io=file_path + dir_list[0], sheet_name=str(year), header=1, skipfooter=25)

    # Remove leading spaces for column names
    df.columns = df.columns.str.strip()

    # Rename column names
    df.rename({'Name and Address': 'name',
               'of': 'capacity'},
              axis=1, inplace=True)

    # Remove unnecessary header row
    df = df.iloc[1:]

    # Remove quarterly occupancy/utilization values
    df.drop(df.filter(regex='Avg|%').columns, axis=1, inplace=True)

    # Create column with average occupancy
    df["occupancy"] = df.loc[:, [
        col for col in df if col.startswith('Unnamed')]].mean(axis=1).astype(float).round(0)

    # Remove all month columns
    df.drop(df.filter(regex='Unnamed').columns, axis=1, inplace=True)

    # Remove extra rows from formatted excel workbook
    df = df[(df["name"].str.contains("Subtotal") == False) &
            (df["name"].str.contains("Grand Total") == False) &
            (df['capacity'].notna()) &
            (df['occupancy'].notna())]

    # Remove superscript numbers from lot name column
    df['name'] = df['name'].replace(
        to_replace=r"\b\d+[/,].\d+", value=r"", regex=True)  # remove numbers sep by , or /
    # df['name'] = df['name'].replace(
    #     to_replace=r"\b[ ](\d+)(?!.*\w)", value=r"", regex=True)
    df['name'] = df['name'].replace(
        to_replace=r"(\d+)(?!\w)(?! )(?!\))", value=r"", regex=True)  # remove all numbers at the end of the strings
    df['name'] = df['name'].replace(
        to_replace=r"[ \t]+$", value=r"", regex=True)  # remove trailing spaces

    # Add columns for ownership_status, address, notes
    df['owner_status'] = None
    df['address'] = None
    df['notes'] = None

    # Create 'agency' column with county name as values
    df.insert(0, 'agency', 'Pierce Transit')

    # Ensure all column names are lowercase
    df.columns = df.columns.str.lower()
    
    # remove lots maintained by Sound Transit
    df.drop(df[(df.name == 'Bonney Lake (SR410)') |
               (df.name == 'Lakewood Station') |
               (df.name == 'S. Tacoma Station') |
               (df.name == 'Puyallup Train Station') |
               (df.name == 'Sumner Train Station')].index, inplace=True)
    
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
        sql='select * from park_and_ride.lot_dim', con=sql_conn)

    # facts table
    master_facts_df = pd.read_sql(
        sql='select * from park_and_ride.park_and_ride_facts', con=sql_conn)

    # join so that lots have capacity numbers for checking against new data
    master_df = pd.merge(master_dim_df, master_facts_df,
                         left_on='lot_dim_id', right_on='lot_dim_id',
                         how="inner")

    # filter lots in Pierce County from master df
    pierce_master = master_df[master_df['county_name'].str.contains('Pierce')]

    # merge data frames - keep only the current records to determine which ones don't line up with the master list
    pierce_lots_merge = pd.merge(pierce_master, df,
                                 left_on='lot_name', right_on='name',
                                 how="right")

    # remove lots that are in master and do not match in Pierce Transit data
    maybe_new_lots = pierce_lots_merge[pierce_lots_merge['lot_name'].isnull()]
    
    maybe_new_lots.rename({'capacity_y': 'capacity', 'occupancy_y': 'occupancy'}, axis=1, inplace=True)
    
    maybe_new_lots = maybe_new_lots.loc[:, ['agency', 'owner_status', 'name', 'address', 'capacity', 'occupancy']].sort_values(by='name')

    print('All done.')
    return df, maybe_new_lots
