import os
import pandas as pd
import pyodbc  # for Elmer connection
from sqlalchemy import create_engine  # for Elmer data insert

os.chdir('C:\\Users\\GGibson\\GitHub\\PSRC\\park-ride')

# processing functions
import process_community_transit as ct
import process_king_county_metro as kcm
import process_kitsap_transit as kt
import process_pierce_transit as pt
import process_sound_transit as st
import process_combined_data as com

# connection string for Elmer
conn_string = (
    r'Driver=SQL Server;'
    r'Server=AWS-Prod-SQL\Sockeye;'
    r'Database=Elmer;'
    r'Trusted_Connection=yes;'
)

#---------------------------------------------------------------------------------------------------
# Process King County Metro data and clean names
king_data, king_new_lots = kcm.process_king_county_metro(2023)

# rename 33 'new' lots - those in the new data set that don't match the master list
king_data = king_data.replace(
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
              'Olson Place SW / Myers Way': 'Olson Place SW/Myers Way',
              'Renton Municipal Garage P&R': 'Renton City Municipal Garage',
              'Renton P&R (Metropolitan Place Apts)': 'Renton P&R (Metropolitan Place)',
              'S Mercer Center-Mercer Island QFC P&R': 'South Mercer Center, Mercer Island QFC',
              'Shoreline': 'Shoreline P&R',
              'South Federal Way': 'South Federal Way P&R',
              # combine garage and surface
              'South Kirkland (Garage)': 'South Kirkland P&R',
              'South Sammamish': 'South Sammamish P&R',
              'St. Luke\'s Lutheran Church - Federal Way': 'St. Luke\'s Lutheran Church-Federal Way',
              'The Vine Church (formerly Bethany Bible)': 'The Vine Church',
              'Tibbetts Valley Park': 'Tibbett\'s Valley Park',
              'Tukwila': 'Tukwila P&R'}
     })

# group by name and recalculate/rebuild
king_data = king_data.groupby(['name'], as_index=False).agg(
    capacity = ('capacity', 'sum'),
    occupancy = ('occupancy', 'sum'))

# Create 'agency' column with county name as values
king_data.insert(0, 'agency', 'King County Metro Transit')

# Add column for ownership_status, address, notes
king_data['owner_status'] = None
king_data['address'] = None
king_data['notes'] = None

#---------------------------------------------------------------------------------------------------
# Process Kitsap Transit data and clean names
kitsap_data, kitsap_new_lots = kt.process_kitsap_transit(2023)

# rename 13 'new' lots - those in the new data set that don't match the master list
kitsap_data = kitsap_data.replace(
    {'name': {'1st United Methodist Church': 'First United Methodist Church',
              'Annapolis Park & Ride': 'Annapolis P&R',
              'Burly Bible Church': 'Burley Bible Church',
              'Crossroads Church': 'Crossroads Neighborhood Church',
              'Day Road & SR 305': 'Day Rd & SR 305',
              'Gateway Center': 'Gateway',
              'George\'s Corners': 'George\'s Corner',
              'Harper Free Evangelical Church': 'Harper Evangelical Free Church',
              'McWilliams Park & Ride': 'McWilliams P&R',
              'Mullenix and Highway 16': 'Mullenix Road P&R',
              'North Base Park & Ride': 'North Base',
              'Olalla Valley Fire Station': 'Olalla Valley',
              'Poulsbo Juntion': 'Poulsbo Junction'}
     })

#---------------------------------------------------------------------------------------------------
# Process Pierce Transit data and clean names
pierce_data, pierce_new_lots = pt.process_pierce_transit(2023)

# rename 10 'new' lots - those in the new data set that don't match the master list
pierce_data = pierce_data.replace(
    {'name': {'72nd St. Transit Center': '72nd St Transit Center',
              'Center St': 'Center Street',
              'DuPont': 'Dupont Station',
              'Narrows/Skyline': 'Narrows P&R',
              'North Gig Harbor (Kimball Drive)': 'Kimball Dr P&R',
              'Puyallup Red lot': 'Puyallup Red Lot',
              'South Purdy': 'South Purdy P&R',
              'South Tacoma East I (north side)': 'South Tacoma East 1 (North side)',
              'South Tacoma East II (south side)': 'South Tacoma East 2 (South side)'}
     })

#---------------------------------------------------------------------------------------------------
# Process Community Transit data and clean names
community_data, community_new_lots = ct.process_community_transit(2023)

# rename 13 'new' lots - those in the new data set that don't match the master list
community_data = community_data.replace(
    {'name': {'Arlington': 'Arlington P&R',
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
              'South Everett': 'South Everett Freeway Station'}
     })

#---------------------------------------------------------------------------------------------------
# Process Sound Transit data and clean names
sound_data, sound_new_lots = st.process_sound_transit(2023)

# rename 15 'new' lots - those in the new data set that don't match the master list
sound_data = sound_data.replace(
    {'name': {'Auburn Garage': 'Auburn Garage at Auburn Station',
              'Auburn Surface Parking Lot': 'Auburn Surface Lot at Auburn Station',
              'Bonney Lake': 'Bonney Lake South (SR 410)',
              'Edmonds (Ft. Wayne)': 'Edmonds Station Leased Lot Salish Crossings',
              'Federal Way TC': 'Federal Way Transit Center',
              'Issaquah TC': 'Issaquah Transit Center',
              'Kent Garage': 'Kent Garage at Kent Station',
              'Kent Surface Parking Lot': 'Kent Surface Lot at Kent Station',
              'Lynnwood TC Garage': 'Lynnwood Transit Center',
              'Mercer Island': 'Mercer Island P&R',
              'Puyallup Station': 'Puyallup Train Station',
              'South Bellevue': 'South Bellevue P&R',
              'Sumner Station': 'Sumner Train Station',
              'Tukwila Station': 'Tukwila Sounder Station',
              'Tukwila Station (TIBS)': 'Tukwila International Blvd Station'}
     })

# New lots ----------------------------
# BelRed Station, added in Dec 2023
# Redmond Technology Center Garage (RTS), added in Dec 2023

#---------------------------------------------------------------------------------------------------
# Combine datasets
processed_tables = [king_data, kitsap_data, pierce_data, community_data, sound_data]

combined_data, owner_check, lot_id_check = com.combine_processed_data(processed_tables, 2023)

# Subset final data for insert into fact table in Elmer
data_upload = combined_data.loc[:, ['lot_dim_id', 'data_year', 'capacity', 'occupancy', 'notes']].sort_values('lot_dim_id')

# Create sqlalchemy engine for table insert in Elmer
engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(conn_string))

# FINAL STEP ---------------------------------------------------------------------------------------
# Insert new data into fact table in Elmer
# Output displays '-1' which means the dataframe has multiple rows
data_upload.to_sql(name='park_and_ride_facts',
                   con=engine,
                   schema='park_and_ride',
                   if_exists='append',
                   index=False
                   )
