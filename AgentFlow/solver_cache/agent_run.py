import pandas as pd

# Load the source data
source1 = pd.read_csv('/path/to/test_96_0.csv', index_col=0)
lookup_table = pd.read_csv('/path/to/lookup_table.csv', index_col=0)

# Step 1: JOIN - Join Source1_96_0 with the embedded lookup table on the 'Publisher' string column
joined_df = source1.merge(lookup_table, on='Publisher', how='inner')

# Step 2: PROJECT - Select the integer 'Publisher' column from the join result as Target1_96
target_df = joined_df[['Publisher']].rename(columns={'Publisher': 'Target1_96'})

# Step 3: OUTPUT - Save the resulting target table to the specified CSV path
target_df.to_csv('/path/to/output_target.csv', index=False)