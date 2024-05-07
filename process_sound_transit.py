import os
import pandas as pd
import numpy as np
import pyodbc  # for Elmer connection

def process_sound_transit(year):
    """Pulls Sound Transit files from folder using current project year and combines into one table.
    
    Each monthly file contains observed parking counts for Tuesday-Thursday.
    Daily counts are averaged per month, then months are combined and averaged
    per year.
    """
    
    print('Begin processing monthly Sound Transit park & ride data.')
    
    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/' + str(year) + '/Sound Transit/XLSX/'
    dir_list = os.listdir(file_path)
    
    # Loop through monthly files in folder and join months one by one
    processed = pd.DataFrame()
    for i in dir_list:
        if 'july' in i.lower():
            df = pd.read_excel(io=file_path + i, skipfooter=2)
        elif 'feb' in i.lower():
            df = pd.read_excel(io=file_path + i, skiprows=[1], skipfooter=3)
        else:
            df = pd.read_excel(io=file_path + i, skipfooter=4)
            
        month = list(df.columns.values)
        month = month[2][:3].lower()
        
        if month in ['jul', 'jun']:
            # Remove 'Mon Year ' from column names; replace spaces with _ in names and lowercase
            df.columns = df.columns.str.replace(r'(\w{3}\s+\d{4}\s+)', '', regex=True).str.strip()
            df.columns = df.columns.str.replace(' ', '_', regex=True).str.lower()
            
            # Rename 'usage' column
            df.rename({'usage': 'occupancy'}, axis=1, inplace=True)
        else:
            # Remove 'Mon Year ' and 'Usage ' from column names; replace spaces with _ in names and lowercase
            df.columns = df.columns.str.replace(r'(\w{3}\s+\d{4}\s+)', '', regex=True).str.replace(r'Usage\s', '', regex=True)
            df.columns = df.columns.str.replace(' ', '_', regex=True).str.lower()

            # Create column of avg occupied spaces; recode service_type; add agency column
            df = df.assign(occupancy = df.loc[:, ['tuesday', 'wednesday', 'thursday']].mean(axis=1).round(0))

        df['service_type'] = np.where(df['service_type'].str.contains('^leas', case=False, regex=True), 'leased', 'permanent')

        # Subset df to only needed columns
        df = df.loc[:, ['location', 'service_type', 'address', 'capacity', 'occupancy']]

        # Rename columns to standard names
        df.rename({'location':'name',
                    'service_type':'owner_status',
                    'capacity':'c_' + month,
                    'occupancy':'o_' + month},
                   axis=1, inplace=True)
        
        # Strip leading/trailing whitespace from lot names
        df['name'] = df['name'].map(lambda x: x.strip())
        
        if len(processed.columns) == 0:
            processed = df.copy(deep=True)
        else:
            processed = pd.merge(processed, df, how='outer', on=['name', 'owner_status', 'address'])
        
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
    
    # Subset dataframe to needed columns for output; insert notes, agency name
    processed = processed.loc[:, ['name', 'owner_status', 'address', 'capacity', 'occupancy']].sort_values(by='name')
    processed['notes'] = None
    processed.insert(0, 'agency', 'Sound Transit')
    
    # remove lots that are maintained by other agencies
    processed = processed.drop(processed[(processed.name in ('Auburn Station',
                                                             'DuPont',
                                                             'Eastmont',
                                                             'Kent Station',
                                                             'Puyallup Red Lot (Fairgrounds)',
                                                             'Puyallup Station',
                                                             'South Hill',
                                                             'Sumner Station',
                                                             'Tacoma Dome Station Garage'
                                                             ))].index)
    
    # Auburn Station - combined from surface parking lot and auburn garage, does not exist in master
    # DuPont: belongs to Pierce Transit
    # Eastmont: belongs to Community Transit
    # Kent Station: combination of Kent Garage and Kent Surface Parking Lot
    # Puyallup Red Lot (Fairgrounds): belongs to Pierce Transit
    # Puyallup Station: Puyallup Train Station is the same lot and belongs to Pierce Transit
    # South Hill: belongs to Pierce Transit as South Hill P&R
    # Sumner Station: belongs to Pierce Transit as Sumner Train Station
    # Tacoma Dome Station Garage: belongs to Pierce Transit as Tacoma Dome Station
    
    print('Connecting to Elmer to pull master data park and ride lots')
    # connect to master data
    conn_string = (
        r'Driver=SQL Server;'
        r'Server=AWS-Prod-SQL\Sockeye;'
        r'Database=Elmer;'
        r'Trusted_Connection=yes;'
    )

    sql_conn = pyodbc.connect(conn_string)

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
