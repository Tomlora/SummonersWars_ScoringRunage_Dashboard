import streamlit as st
import pandas as pd

from streamlit_filter_tree import condition_tree, config_from_dataframe

# Initial dataframe
df = pd.DataFrame({
    'First Name': ['Georges', 'Alfred'],
    'Age': [45, 98],
    'Favorite Color': ['Green', 'Red'],
    'Like Tomatoes': [True, False]
})

# Basic field configuration from dataframe
config = config_from_dataframe(df)

# Condition tree
query_string = condition_tree(config)

# Filtered dataframe
df = df.query(query_string)
