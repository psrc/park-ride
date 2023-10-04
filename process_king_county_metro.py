import pandas as pd
import os
import pyodbc  # for Elmer connection


def process_king_county_metro():
    """Process 2022 park & ride data from King County Metro Transit."""

    print('Begin processing King County Metro Transit park & ride data.')

    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/2022/King County/'
    dir_list = os.listdir(file_path)

    # Read xlsx file in folder
    df = pd.read_excel(
        io=file_path + dir_list[0], sheet_name=0, usecols='A:D', skipfooter=1)

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

    print('All done.')
    return df


def clean_names_king_county_metro():
    """Clean names of 2022 park & ride lots from King County Metro to match master data."""

    print('Begin renaming process for aligning King County Metro park & ride data.')

    # view data from King County Metro
    king_data = process_king_county_metro()

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
    # master_df2 = master_df.drop_duplicates(subset=['lot_dim_id'])

    # print names of columns in master dataframe
    # print(master_df.columns.tolist())

    # remove lots from Sound Transit
    king_master = master_df[master_df['maintainer_agency'].isin(
        ['King County Metro Transit'])]

    # merge data frames - keep only the 2022 records to determine which ones don't line up with the master list
    king_lots_merge22 = pd.merge(king_master, king_data,
                                 left_on='lot_name', right_on='name',
                                 how="right")

    # remove lots that are in master and do not match in Pierce data - this step is for checking lots
    maybe_new_lots = king_lots_merge22[king_lots_merge22['lot_name'].isnull()]

    print('Renaming lots with inconsistent names')
    # rename 46 'new' lots - those in the new data set that don't match the master list
    king_data_renamed = king_data.replace(
        {'name': {'Auburn': 'Auburn P&R',
                  'Bear Creek': 'Bear Creek P&R',
                  'Bothell': 'Bothell P&R',
                  'Brickyard Rd': 'Brickyard Road P&R',
                  'Burien TC': 'Burien Transit Center',
                  'Church by the Side of the Road (THE)': 'Church by the Side of the Road',
                  'Duvall': 'Duvall P&R',
                  'East Hill Friends': 'East Hill Friends Church',
                  # combine garage with Eastgate P&R
                  'Eastgate (Garage)': 'Eastgate P&R',
                  'Federal Way / S 320th Street P&R': 'Federal Way/S 320th St',
                  'Greenlake / I-5 & 65th St.': 'Greenlake (I-5/NE 65th St)',
                  'Issaquah Highlands': 'Issaquah Highlands P&R',
                  'Kent / Des Moines': 'Kent/Des Moines',
                  'Kent / James Street': 'Kent/James Street',
                  'Kingsgate P&R (WSDOT)': 'Kingsgate P&R',
                  'Kirkland Way': 'SR 908/Kirkland Way',
                  'Lake Meridian': 'Lake Meridian/East Kent',
                  'New Life Church @ Renton': 'New Life Church',
                  'Newport Hills': 'Newport Hills P&R',
                  'North Bend': 'North Bend P&R',
                  'North Seattle': 'North Seattle Interim',
                  'Northgate Transit Center': 'Northgate TC Extension',
                  'Olson Place SW / Myers Way': 'Olson Place SW/Myers Way',
                  'Renton Municipal Garage P&R': 'Renton City Municipal Garage',
                  'Renton P&R (Metropolitan Place Apts)': 'Renton P&R (Metropolitan Place)',
                  'S Mercer Center-Mercer Island QFC P&R': 'South Mercer Center, Mercer Island QFC',
                  'SW Spokane': 'SW Spokane St',
                  'Shoreline': 'Shoreline P&R',
                  'South Federal Way': 'South Federal Way P&R',
                  # combine garage and surface
                  'South Kirkland (Garage)': 'South Kirkland P&R',
                  # combine garage and surface
                  'South Kirkland (Surface)': 'South Kirkland P&R',
                  'South Sammamish': 'South Sammamish P&R',
                  'St. Luke\'s Lutheran Church - Federal Way': 'St. Luke\'s Lutheran Church-Federal Way',
                  'The Vine Church (formerly Bethany Bible)': 'The Vine Church',
                  'Tibbetts Valley Park': 'Tibbett\'s Valley Park',
                  'Tukwila': 'Tukwila P&R'}
         })

    # group by name and recalculate/rebuild
    king_data_renamed = king_data_renamed.groupby(['name'], as_index=False).agg(
        capacity = ('capacity', 'sum'),
        occupancy = ('occupancy', 'sum'))

    # Create 'agency' column with county name as values
    king_data_renamed.insert(0, 'agency', 'King County Metro Transit')

    # Add column for ownership_status, address, notes
    king_data_renamed['owner_status'] = None
    king_data_renamed['address'] = None
    king_data_renamed['notes'] = None

    return king_data_renamed
