import os
import pandas as pd
import numpy as np
import pyodbc  # for Elmer connection

def process_sound_transit(config):
    """Pulls Sound Transit files from folder using current project year and combines into one table.
    
    Each monthly file contains observed parking counts for Tuesday-Thursday.
    Daily counts are averaged per month, then months are combined and averaged
    per year.
    """
    
    print('Begin processing monthly Sound Transit park & ride data.')
    
    # Assign path to agency in project folder; create list of files in folder
    file_path = config['project_path'] + str(config['year']) + '/Sound Transit/'
    dir_list = os.listdir(file_path)

    workbook = pd.ExcelFile(file_path + dir_list[0])
    wk_sheets = workbook.sheet_names[6:]
    wk_sheets = [i for i in wk_sheets if not i.endswith(('ADA', 'ADA ', 'ADA  '))]
    
    # Loop through monthly files in folder and join months one by one
    processed = pd.DataFrame()
    for i in wk_sheets:
        df = workbook.parse(sheet_name=i, skipfooter=3)
        month = i[:3].lower()
        
        # Remove 'Year ' from column names; replace spaces with _ in names and lowercase
        df.columns = df.columns.str.replace(r'(\d{4}\s+)', '', regex=True).str.strip()
        df.columns = df.columns.str.replace(' ', '_', regex=True).str.lower()

        # Rename 'usage' column
        df.rename({'usage': 'occupancy'}, axis=1, inplace=True)

        # Remove NA rows
        df.dropna(subset='location', inplace=True)

        # Strip leading/trailing whitespace from lot names
        df['location'] = df['location'].map(lambda x: x.strip())

        # Rows to delete
        del_rows = ('NORTH', 'SOUTH', 'EAST')
        df = df[~df['location'].isin(del_rows)]

        # Subset df to only needed columns
        df = df.loc[:, ['location', 'address', 'capacity', 'occupancy']]
        
        # Fix Puyallup names and combine
        #df.replace(
        #    {'location': {'Puyallup Garage': 'Puyallup Train Station',
        #                  'Puyallup Station Suface Lots': 'Puyallup Train Station',
        #                  'Puyallup Surface Lot E': 'Puyallup Train Station'}},
        #    {'address': {'500 2nd Avenue NW, Puyallup 98371': '131 W Main Street, Puyallup 98371',
        #                 '598 2nd Avenue NW, Puyallup 98371': '131 W Main Street, Puyallup 98371'}},
        #    inplace=True)
        
        #df = df.groupby(['location', 'address'], as_index=False).agg(
        #    capacity = ('capacity', 'sum'),
        #    occupancy = ('occupancy', 'sum')
        #)

        # Rename columns to standard names
        df.rename({'location':'name',
                   'capacity':'c_' + month,
                   'occupancy':'o_' + month},
                   axis=1, inplace=True)
        
        if len(processed.columns) == 0:
            processed = df.copy(deep=True)
        else:
            processed = pd.merge(processed, df, how='outer', on=['name', 'address'])
        
        print('Done processing {} data.'.format(month))
        
    # Average monthly usage to annual
    processed = processed.assign(capacity = processed.loc[:, ['c_jan', 'c_feb', 'c_mar',
                                                              'c_apr', 'c_may', 'c_jun',
                                                              'c_jul', 'c_aug', 'c_sep',
                                                              'c_oct', 'c_nov', 'c_dec']].mean(axis=1).round(0))
    
    processed = processed.assign(occupancy = processed.loc[:, ['o_jan', 'o_feb', 'o_mar',
                                                               'o_apr', 'o_may', 'o_jun',
                                                               'o_jul', 'o_aug', 'o_sep',
                                                               'o_oct', 'o_nov', 'o_dec']].mean(axis=1).round(0))
    
    # Subset dataframe to needed columns for output; insert ownership, notes, agency name
    processed = processed.loc[:, ['name', 'address', 'capacity', 'occupancy']].sort_values(by='name')
    processed['owner_status'] = ''
    processed['notes'] = None
    processed.insert(0, 'agency', 'Sound Transit')
    
    # remove lots that are maintained by other agencies or other reasons
    processed.drop(processed[#(processed.name == 'Auburn Station') |
                             (processed.name == 'DuPont') |
                             #(processed.name == 'Eastmont') |
                             #(processed.name == 'Kent Station') |
                             #(processed.name == 'Puyallup Garage') |
                             #(processed.name == 'Puyallup Station Suface Lots') |
                             #(processed.name == 'Puyallup Station Surface Lots') |
                             #(processed.name == 'Puyallup Surface Lot E') |
                             (processed.name == 'South Everett Freeway Station') |
                             (processed.name == 'South Hill') |
                             (processed.name == 'Tacoma Dome Station Garage')
                             ].index, inplace=True)
    
    # Auburn Station - combined from surface parking lot and auburn garage, does not exist in master
    # DuPont: belongs to Pierce Transit
    # Eastmont: belongs to Community Transit
    # Kent Station: combination of Kent Garage and Kent Surface Parking Lot
    # Puyallup Garage: capacity part of Puyallup Train Station
    # Puyallup Station Suface/Surface Lots: capacity part of Puyallup Train Station
    # Puyallup Surface Lot E: capacity part of Puyallup Train Station
    # South Everett Freeway Station: belongs to Community Transit
    # South Hill: belongs to Pierce Transit as South Hill P&R
    # Tacoma Dome Station Garage: belongs to Pierce Transit as Tacoma Dome Station

    # Drop extraneous Marymoor station rows
    processed.drop(processed[(processed.name == 'Marymoor station') & (processed.capacity < 1400)].index, inplace=True)
    
    print('Connecting to Elmer to pull master data park and ride lots')
    # connect to master data
    sql_conn = pyodbc.connect(config['conn_string'])

    # dim table
    master_dim_df = pd.read_sql(
        sql="select * from park_and_ride.lot_dim where maintainer_agency = 'Sound Transit'", con=sql_conn)

    # facts table
    master_facts_df = pd.read_sql(
        sql='select * from park_and_ride.park_and_ride_facts', con=sql_conn)

    # join so that lots have capacity numbers for checking against new data
    master_df = pd.merge(master_dim_df, master_facts_df,
                         left_on='lot_dim_id', right_on='lot_dim_id',
                         how="inner")
    
    # merge data frames - keep only current records to determine which ones don't line up with the master list
    sound_lots_merge = pd.merge(master_df, processed,
                                left_on='lot_name', right_on='name',
                                how="right")

    maybe_new_lots = sound_lots_merge[sound_lots_merge['lot_name'].isnull()]
    
    maybe_new_lots.rename({'capacity_y': 'capacity', 'occupancy_y': 'occupancy'}, axis=1, inplace=True)
    
    maybe_new_lots = maybe_new_lots.loc[:, ['agency', 'owner_status', 'name', 'address', 'capacity', 'occupancy']].sort_values(by='name')
    
    print('All done.')
    return processed, maybe_new_lots
