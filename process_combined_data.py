import pandas as pd
import pyodbc  # for Elmer connection

def combine_processed_data(table_list, year):
    """Combines processed park & ride datasets and prepares for insertion into Elmer facts table."""
    
    # Only run if there are five datasets passed to the function
    if len(table_list) == 5:
        print('Processing data to prepare for insertion into Elmer.')
        
        # Combine data from agencies, then sort and strip leading/trailing spaces from names
        df = pd.concat(table_list).sort_values(by=['name'])
        df['name'] = df['name'].map(lambda x: x.strip())
        
        # Combine processed data with dim table from Elmer
        conn_string = (
            r'Driver=SQL Server;'
            r'Server=AWS-Prod-SQL\Sockeye;'
            r'Database=Elmer;'
            r'Trusted_Connection=yes;'
        )

        sql_conn = pyodbc.connect(conn_string)

        # dim table
        master_dim_df = pd.read_sql(sql='select * from park_and_ride.lot_dim', con=sql_conn)
        
        final_data = pd.merge(df, master_dim_df,
                              left_on='name', right_on='lot_name',
                              how='left')
        
        final_data.rename({'notes_x': 'notes',
                           'notes_y': 'lot_dim_notes'},
                          axis=1, inplace=True)
        
        # Add data year to final data
        final_data.insert(0, 'data_year', year)
        
        # Check data
        owner_check = final_data.loc[:, ['agency', 'name', 'owner_status', 'ownership_status', 'lot_name']].sort_values('owner_status')
        lot_id_check = final_data[final_data.duplicated('lot_dim_id', keep=False)]
        
        return final_data, owner_check, lot_id_check
    
    else:
        print("The supplied list does not have the correct number of datasets.")
