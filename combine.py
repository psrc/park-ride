import os
import pandas as pd
import numpy as np
import pyodbc  # for Elmer connection

# working directory
print(os.getcwd())
os.chdir("C:\\Users\\mrichards\\Documents\\GitHub\\park-ride")


def process_combining_agency_data():
    """Process 2022 park & ride data from PSRC transit agencies."""

    print('Begin processing combining and cleaning park & ride data.')

    from process_community_transit import clean_names_community_transit
    from process_king_county_metro import clean_names_king_county_metro
    from process_kitsap_transit import clean_names_kitsap_transit
    from process_pierce_transit import clean_names_pierce_transit
    from process_sound_transit import process_sound_transit

    # Combine data from agencies
    combined = pd.concat([clean_names_community_transit(),
                          clean_names_king_county_metro(),
                          clean_names_kitsap_transit(),
                          clean_names_pierce_transit(),
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


def clean_names_sound_transit():
    """Clean names of 2022 park & ride lots from Sound Transit to match master data."""

    print('Begin renaming process for aligning Sound Transit park & ride data.')

    process_combining_agency_data()

    conn_string = conn_str = (
        r'Driver=SQL Server;'
        r'Server=AWS-Prod-SQL\Sockeye;'
        r'Database=Elmer;'
        r'Trusted_Connection=yes;'
    )

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

    # check_names of columns for join/merge
    output2.columns.to_list()  # name
    master_dim_df.columns.to_list()  # lot_name

    # merge data frames - keep only the 2022 records to determine which ones don't line up with the master list
    lots_merge22 = pd.merge(master_df, output2, left_on='lot_name',
                            right_on='name', how="right")

    lots_check = lots_merge22[lots_merge22['lot_name'].isnull()]
    # 25 lots from Sound Transit that don't line up with master list - requires checking before can resolve

    # edit data to fix Sound Transit issues
    sound_data_renamed = output2({'name': {'72nd St. Transit Center': '72nd St Transit Center',
                                           'Auburn Garage': 'Auburn Garage at Auburn Station',
                                           'Auburn Surface Parking Lot': 'Auburn Surface lot at Auburn Station',
                                           'Bonney Lake': 'Bonney Lake South (SR 410)',
                                           'Edmonds Salish Crossings': 'Edmonds Station Leased Lot Salish Crossings',
                                           'Federal Way TC': 'Federal Way Transit Center',
                                           'Issaquah TC': 'Issaquah Transit Center',
                                           'Kent Garage': 'Kent Garage at Kent Station',
                                           'Kent Surface Parking Lot': 'Kent Surface Lot at Kent Station',
                                           'Lynnwood TC': 'Lynnwood Transit Center',
                                           'Mercer Island': 'Mercer Island P&R',
                                           'South Bellevue': 'South Bellevue P&R',
                                           'Tukwila Station': 'Tukwila Sounder Station',
                                           'Tukwila Station (TIBS)': 'Tukwila International Blvd Station'}})


# ISSUES -------------

# within Sound Transit data ..................
# Auburn Station - combined from surface parking lot and auburn garage, does not exist in master so can be removed from ST
# DuPont: belongs to Pierce Transit - remove from Sound Transit
# Eastmont: belongs to Community Transit - remove from Sound Transit
# 'Edmonds Salish Crossings': split from Edmonds Station beginning 2014 -> add/edit fact records
# 'Federal Way TC': 'Federal Way Transit Center'
# Kent Station: combination of Kent Garage and Kent Surface Parking Lot - remove from Sound Transit
# Puyallup Red Lot (Fairgrounds): belongs to Pierce Transit - remove from Sound Transit
# Puyallup Station: Puyallup Train Station is the same lot and belongs to Pierce Transit - remove from Sound Transit
# South Hill: belongs to Pierce Transit as South Hill P&R - remove from Sound Transit
# Sumner Station: belongs to Pierce Transit as Sumner Train Station - remove from Sound Transit
# Tacoma Dome Station Garage: belongs to Pierce Transit as Tacoma Dome Station - remove from Sound Transit
