# Importing external library
import numpy as np
import pandas as pd
import os

# Combine data from agencies
from process_community_transit import process_community_transit
from process_king_county_metro import process_king_county_metro
from process_kitsap_transit import process_kitsap_transit
from process_pierce_transit import process_pierce_transit
from process_sound_transit import process_sound_transit


output = pd.concat([process_community_transit(),
                    process_king_county_metro(),
                    process_kitsap_transit(),
                    process_pierce_transit(),
                    process_sound_transit()])

# Find any overlapping entries, prioritize agencies before Sount Transit
