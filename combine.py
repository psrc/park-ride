from process_community_transit import process_community_transit
from process_king_county_metro import process_king_county_metro
from process_kitsap_transit import process_kitsap_transit
from process_pierce_transit import process_pierce_transit
from process_sound_transit import process_sound_transit
import numpy as np
import pandas as pd
import os

# check working directory
print(os.getcwd())
os.chdir("C:\\Users\\mrichards\\Documents\\GitHub\\park-ride")

# Importing external library


# Combine data from agencies
output = pd.concat([process_community_transit(),
                    process_king_county_metro(),
                    process_kitsap_transit(),
                    process_pierce_transit(),
                    process_sound_transit()])

# output.head(3)

# Find any overlapping entries, prioritize agencies before Sount Transit
output2 = output.sort_values(by=['name'])

# Selecting duplicate rows
duplicate = output2[output2.duplicated('name')]

print("Duplicate Rows :")

# Print the resultant Dataframe
duplicate
