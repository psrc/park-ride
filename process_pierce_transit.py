import pandas as pd
import os
import pyodbc  # for Elmer connection


def process_pierce_transit():
    """Process 2022 park & ride data from Pierce Transit."""

    print('Begin processing Pierce Transit park & ride data.')

    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/2022/Pierce Transit/'
    dir_list = os.listdir(file_path)

    # Read xlsx file in folder
    df = pd.read_excel(
        io=file_path + dir_list[0], sheet_name='2022',  header=1, skipfooter=25)

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

    # Create column with average occupancy
    df["occupied_spaces"] = df.loc[:, [
        col for col in df if col.startswith('Unnamed')]].mean(axis=1)

    # Remove all month columns
    df.drop(df.filter(regex='Unnamed').columns, axis=1, inplace=True)

    # Convert object type to float
    df['total_spaces'] = df['total_spaces'].astype(float)
    df['occupied_spaces'] = df['occupied_spaces'].astype(float)

    # Calculate utilization rate
    df['utilization'] = df['occupied_spaces']/df['total_spaces']

    # Remove extra rows from formatted excel workbook
    df = df[(df["name"].str.contains("Subtotal") == False) &
            (df['total_spaces'].notna()) &
            (df['occupied_spaces'].notna())]

    # Remove superscript numbers from lot name column
    df['name'] = df['name'].replace(
        to_replace=r"\b\d+[/,].\d+", value=r"", regex=True)  # remove numbers sep by , or /
    # df['name'] = df['name'].replace(
    #     to_replace=r"\b[ ](\d+)(?!.*\w)", value=r"", regex=True)
    df['name'] = df['name'].replace(
        to_replace=r"(\d+)(?!\w)(?! )(?!\))", value=r"", regex=True)  # remove all numbers at the end of the strings
    df['name'] = df['name'].replace(
        to_replace=r"[ \t]+$", value=r"", regex=True)  # remove trailing spaces

    # Add column for ownership_status
    df['owner_status'] = ''
    df['address'] = ''

    # Create 'agency' column with county name as values
    df.insert(0, 'agency', 'Pierce Transit')

    # Ensure all column names are lowercase
    df.columns = df.columns.str.lower()

    print('All done.')
    return df


def clean_names_pierce_transit():
    """Clean names of 2022 park & ride lots from Pierce Transit to match master data."""

    print('Begin renaming process for aligning Pierce Transit park & ride data.')

    # view data from Pierce Transit
    pierce_data = process_pierce_transit()

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
    # master_df2 = master_df.drop_duplicates(subset=['lot_dim_id'])

    # print names of columns in master dataframe
    # print(master_df.columns.tolist())

    # filter lots in Pierce County from master df
    pierce_master = master_df[master_df['county_name'].str.contains('Pierce')]
    # pierce_master = master_df[master_df['maintainer_agency'].isin(['Pierce Transit', 'WSDOT'])]

    # merge data frames - keep only the 2022 records to determine which ones don't line up with the master list
    pierce_lots_merge22 = pd.merge(pierce_master, pierce_data,
                                   left_on='lot_name', right_on='name',
                                   how="right")

    # remove lots that are in master and do not match in Pierce data
    # this step and the next should be run manually before running the function
    maybe_new_lots = pierce_lots_merge22[pierce_lots_merge22['lot_name'].isnull()]

    print('Renaming lots with inconsistent names')
    # rename 10 'new' lots - those in the new data set that don't match the master list
    pierce_data_renamed = pierce_data.replace(
        {'name': {'72nd St. Transit Center': '72nd St Transit Center',
                  'Center St': 'Center Street',
                  'DuPont': 'Dupont Station',
                  'Narrows/Skyline': 'Narrows P&R',
                  'North Gig Harbor (Kimball Drive)': 'Kimball Dr P&R',
                  'Puyallup Red lot': 'Puyallup Red Lot',
                  'S. Tacoma Station': 'South Tacoma Station',
                  'South Purdy': 'South Purdy P&R',
                  'South Tacoma East I (north side)': 'South Tacoma East 1 (North side)',
                  'South Tacoma East II (south side)': 'South Tacoma East 2 (South side)'}
         })
    
    # remove Bonney Lake lot - used in Sound Transit data instead
    pierce_data_renamed = pierce_data_renamed.drop(pierce_data_renamed[pierce_data_renamed.name == 'Bonney Lake (SR410)'].index)

    return pierce_data_renamed
