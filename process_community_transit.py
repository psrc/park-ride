import pandas as pd
import os
import pyodbc  # for Elmer connection


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
    df.drop(['Unnamed: 0', 'AVG_Utilization'], axis=1, inplace=True)

    # Remove leading spaces for column names
    df.columns = df.columns.str.strip()

    # Rename column names
    df.rename({'Facility_Type': 'owner_status',
               'Facility': 'name',
               'Facility_Address': 'address',
               'AVG_Stall_Count': 'total_spaces',
               'AVG_Parked_Vehicles': 'occupied_spaces'},
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
    df.insert(0, 'agency', 'Community Transit')

    # Ensure all column names are lowercase
    df.columns = df.columns.str.lower()

    print('All done.')
    return df


def clean_names_community_transit():
    """Clean names of 2022 park & ride lots from Community Transit to match master data."""

    print('Begin renaming process for aligning Community Transit park & ride data.')

    # view data from Pierce Transit
    community_data = process_community_transit()

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

    # filter lots in Community County from master df
    # community_master = master_df[master_df['county_name'].str.contains('Snohomish')] # also pulls lots from Sound Transit
    community_master = master_df[master_df['maintainer_agency'].isin(['Community Transit'])]

    # merge data frames - keep only the 2022 records to determine which ones don't line up with the master list
    community_lots_merge22 = pd.merge(community_master, community_data,
                                      left_on='lot_name', right_on='name',
                                      how="right")

    # remove lots that are in master and do not match in Pierce data - this step is for checking lots
    maybe_new_lots = community_lots_merge22[community_lots_merge22['lot_name'].isnull()]

    print('Renaming lots with inconsistent names')
    # rename 13 'new' lots - those in the new data set that don't match the master list
    community_data_renamed = community_data.replace({'name': {'Arlington': 'Arlington P&R',
                                                              'Canyon Park': 'Canyon Park P&R',
                                                              'Eastmont': 'Eastmont P&R',
                                                              'Edmonds': 'Edmonds P&R',
                                                              'Freeborn': 'Freeborn Park and Ride',
                                                              'I-5 @ SR 531': 'I-5 at SR 531',
                                                              'Lake Stevens': 'Lake Stevens Transit Center',
                                                              'Mariner': 'Mariner P&R',
                                                              'Marysville Cedar and Grove': 'Marysville at Cedar & Grove',
                                                              'Monroe': 'Monroe P&R',
                                                              'Mountlake Terrace': 'Mountlake Terrace Transit Center',
                                                              'Snohomish': 'Snohomish P&R',
                                                              'South Everett': 'South Everett Freeway Station'}})
    
    # remove Lynnwood lot - used in Sound Transit data instead
    community_data_renamed = community_data_renamed.drop(community_data_renamed[community_data_renamed.name == 'Lynnwood'].index)

    return community_data_renamed
