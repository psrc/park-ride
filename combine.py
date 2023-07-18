import os
import pandas as pd
import numpy as np
import pyodbc  # for Elmer connection

# working directory
# print(os.getcwd())
# os.chdir("C:\\Users\\mrichards\\Documents\\GitHub\\park-ride")


def process_combining_agency_data():
    """Process 2022 park & ride data from PSRC transit agencies."""

    print('Begin processing combining and cleaning park & ride data.')

    from process_community_transit import process_community_transit
    from process_king_county_metro import process_king_county_metro
    from process_kitsap_transit import process_kitsap_transit
    from process_pierce_transit import process_pierce_transit
    from process_sound_transit import process_sound_transit

    # Combine data from agencies
    combined = pd.concat([process_community_transit(),
                          process_king_county_metro(),
                          process_kitsap_transit(),
                          process_pierce_transit(),
                          process_sound_transit()])

    # Sorting data and removing leading/trailing spaces
    global output
    output = combined.sort_values(by=['name'])
    output['name'] = output['name'].map(lambda x: x.strip())

    # Find overlapping entries, prioritize agencies before Sount Transit
    # Selecting duplicate rows
    global duplicate
    duplicate = output[output.duplicated('name', keep=False)]

    # Remove Sound Transit lots within overlap dataframe
    global duplicate2
    duplicate2 = duplicate[duplicate.agency == "Sound Transit"]

    # Merge full dataset, removing Sound Tranist duplicates
    global output2
    output2 = pd.merge(output, duplicate2, indicator=True, how='outer').query(
        '_merge=="left_only"').drop('_merge', axis=1)

    print('Dataframe generated.')
    # return output2


process_combining_agency_data()

conn_string = conn_str = (
    r'Driver=SQL Server;'
    r'Server=AWS-Prod-SQL\Sockeye;'
    r'Database=Elmer;'
    r'Trusted_Connection=yes;'
)
sql_conn = pyodbc.connect(conn_string)
df_names = pd.read_sql(sql='select * from park_and_ride.lot_dim', con=sql_conn)

# check_names of columns for join/merge
output2.columns.to_list()  # name
df_names.columns.to_list()  # lot_name

# merge data frames - keep only the 2022 records to determine which ones don't line up with the master list
lots_merge22 = pd.merge(df_names, output2, left_on='lot_name',
                        right_on='name', how="right")

check = lots_merge22[lots_merge22['lot_name'].isnull()]
