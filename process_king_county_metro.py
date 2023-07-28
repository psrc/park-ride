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
    df = df.groupby(['Name'], as_index=False).agg(total_spaces=('Total Capacity (# of stalls)', 'mean'),
                                                  occupied_spaces=('Mthly - Veh Count', 'mean'))

    # Round decimal values to whole numbers; recalculate utilization
    df = df.round({'occupied_spaces': 0})
    df = df.assign(utilization=df['occupied_spaces']/df['total_spaces'])

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
    # conn_string = conn_str = (
    #     r'Driver=SQL Server;'
    #     r'Server=AWS-Prod-SQL\Sockeye;'
    #     r'Database=Elmer;'
    #     r'Trusted_Connection=yes;')

    # sql_conn = pyodbc.connect(conn_string)

    # dim table
    # master_dim_df = pd.read_sql(
    #     sql='select * from park_and_ride.lot_dim', con=sql_conn)

    # facts table
    # master_facts_df = pd.read_sql(
    #     sql='select * from park_and_ride.park_and_ride_facts', con=sql_conn)

    # join so that lots have capacity numbers for checking against new data
    # master_df = pd.merge(master_dim_df, master_facts_df,
    #                       left_on='lot_dim_id', right_on='lot_dim_id',
    #                       how="inner")
    # master_df2 = master_df.drop_duplicates(subset=['lot_dim_id'])

    # print names of columns in master dataframe
    # print(master_df.columns.tolist())

    # filter lots in Community County from master df
    # king_master = master_df[master_df['county_name'].str.contains('King')] # also pulls lots from Sound Transit
    king_master = master_df[master_df['maintainer_agency'].isin(
        ['King County Metro Transit'])]

    # merge data frames - keep only the 2022 records to determine which ones don't line up with the master list
    king_lots_merge22 = pd.merge(king_master, king_data,
                                 left_on='lot_name', right_on='name',
                                 how="right")

    # remove lots that are in master and do not match in Pierce data - this step is for checking lots
    maybe_new_lots = king_lots_merge22[king_lots_merge22['lot_name'].isnull(
    )]

    print('Renaming lots with inconsistent names')
    # rename 46 'new' lots - those in the new data set that don't match the master list
    king_data_renamed = king_data.replace({'name': {  # 'Auburn (KC)': 'Auburn P&R',
                                                    'Aurora Church of the Nazarene': 'Aurora Church of Nazarene',
                                                    'Aurora Village Transit Center  (KC)': 'Aurora Village Transit Center',
                                                    # 'Bear Creek (KC)': 'Bear Creek P&R',
                                                    # 'Bothell (KC)': 'Bothell P&R',
                                                    'Brickyard Rd': 'Brickyard Road P&R',
                                                    'Burien TC (KC)': 'Burien Transit Center',
                                                    'Church by the Side of the Road (THE)': 'Church by the Side of the Road',
                                                    'Duvall': 'Duvall P&R',
                                                    'East Hill Friends': 'East Hill Friends Church',
                                                    # 'Eastgate (Garage)': 'Eastgate P&R', # check: numbers don't align with Eastgate P&R?
                                                    'Federal Way / S 320th Street P&R': 'Federal Way/S 320th St,
                                                    'Greenlake / I-5 & 65th St.': 'Greenlake (I-5/NE 65th St)',
                                                    # 'Issaquah Highlands (KC)': 'Issaquah Highlands P&R',
                                                    # 'Kenmore Community Club': 'South', # check
                                                    # 'Kenmore P&R (KC)': 'Kenmore P&R',
                                                    'Kent / Des Moines (KC)': 'Kent/Des Moines',
                                                    'Kent / James Street (KC)': 'Kent/James Street',
                                                    'Kingsgate P&R (WSDOT)': 'Kingsgate P&R',
                                                    # 'Kirkland Way': '', # new lot?
                                                    'Lake Meridian (KC)': 'Lake Meridian/East Kent',
                                                    'New Life Church @ Renton': 'New Life Church',
                                                    'Newport Hills': 'Newport Hills P&R',
                                                    'North Bend': 'North Bend P&R',
                                                    # 'North Seattle': 'North Seattle P&R', # check - numbers don't line up
                                                    # 'Northgate Transit Center (KC)': '', # check - numbers/names don't line up
                                                    # 'Ober Park (KC)': 'Ober Park',
                                                    'Olson Place SW / Myers Way (KC)': 'Olson Place SW/Myers Way',
                                                    # 'Redmond P&R (KC)': 'Redmond P&R',
                                                    # 'Redondo Heights P&R (KC)': 'Redondo Heights P&R',
                                                    'Renton Municipal Garage P&R': 'Renton City Municipal Garage',
                                                    'Renton P&R (Metropolitan Place Apts)': 'Renton P&R (Metropolitan Place)',
                                                    'S Mercer Center-Mercer Island QFC P&R': 'South Mercer Center, Mercer Island QFC',
                                                    'SW Spokane': 'SW Spokane St',
                                                    'Shoreline': 'Shoreline P&R',
                                                    # 'South Federal Way (KC)': 'South Federal Way P&R',
                                                    # 'South Kirkland (Garage)': 'Arlington', # check
                                                    # 'South Kirkland (Surface)': 'Arlington', # check
                                                    # 'South Sammamish (KC)': 'South Sammamish P&R',
                                                    'St Columba\'s Episcopal Church': 'St. Columba\'s Episcopal Church',
                                                    'St Luke\'s Lutheran Church - Federal Way': 'St. Luke\'s Lutheran Church-Federal Way',
                                                    'St Matthew Lutheran Church': 'St. Matthew Lutheran Church',
                                                    'The Vine Church (formerly Bethany Bible)': 'The Vine Church',
                                                    'Tibbetts Valley Park': 'Tibbett\'s Valley Park',
                                                    # 'Tukwila (KC)': 'Tukwila P&R',
                                                    # 'Valley Center (KC)': 'Valley Center'}})

    return king_data_renamed
