import os
import pandas as pd
import numpy as np

def process_sound_transit():
    """Pulls 2022 Sound Transit files from folder and combines into one table.
    
    Each monthly file contains observed parking counts for Tuesday-Thursday.
    Daily counts are averaged per month, then months are combined and averaged
    per year.
    """
    
    print('Begin processing monthly Sound Transit park & ride data.')
    
    # Assign path to agency in project folder; create list of files in folder
    file_path = 'J:/Projects/Surveys/ParkRide/Data/2022/Sound Transit/XLSX/'
    dir_list = os.listdir(file_path)
    
    # Loop through monthly files in folder and join months one by one
    processed = pd.DataFrame()
    for i in dir_list:
        if 'oct' in i.lower():
            df = pd.read_excel(io=file_path + i, header=1, skipfooter=3)
        else:
            df = pd.read_excel(io=file_path + i, skipfooter=4)
            
        month = list(df.columns.values)
        month = month[2][:3].lower()

        # Remove 'Mon Year ' and 'Usage ' from column names; replace spaces with _ in names and lowercase
        df.columns = df.columns.str.replace(r'(\w{3}\s\d{4}\s+)', '', regex=True).str.replace(r'Usage\s', '', regex=True)
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
        
        if len(processed.columns) == 0:
            processed = df.copy(deep=True)
        else:
            processed = pd.merge(processed, df, how='left', on=['name', 'owner_status', 'address'])
        
        print('Done processing {} data.'.format(month))
        
    # Average monthly usage to annual
    processed = processed.assign(occupancy = processed.loc[:, ['o_jan', 'o_feb', 'o_mar',
                                                               'o_apr', 'o_may', 'o_jun',
                                                               'o_jul', 'o_aug', 'o_sep',
                                                               'o_oct', 'o_nov', 'o_dec']].mean(axis=1).round(0))
    
    processed = processed.assign(capacity = processed.loc[:, ['c_jan', 'c_feb', 'c_mar',
                                                              'c_apr', 'c_may', 'c_jun',
                                                              'c_jul', 'c_aug', 'c_sep',
                                                              'c_oct', 'c_nov', 'c_dec']].mean(axis=1).round(0))
    
    # Subset dataframe to needed columns for output; insert notes, agency name
    processed = processed.loc[:, ['name', 'owner_status', 'address', 'capacity', 'occupancy']]
    processed['notes'] = None
    processed.insert(0, 'agency', 'Sound Transit')
    
    print('All done.')
    return processed
