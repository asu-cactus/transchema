import pandas as pd
import re

# Read the single source table
df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Extract integer facid by extracting digits from facid string
def facid_to_int(facid):
    digits = re.findall(r'\d+', str(facid))
    if digits:
        return int(''.join(digits))
    else:
        return pd.NA

df['facid_int'] = df['facid'].apply(facid_to_int)

# Group by fac_type and facid_int
# Aggregate capacity by sum (or mean if preferred)
# For other columns (fac_name, fac_address, city_state_zip, owner, operator), aggregate by count to get integer values
agg_df = df.groupby(['fac_type', 'facid_int'], as_index=False).agg({
    'capacity': 'sum',
    'fac_name': 'count',
    'fac_address': 'count',
    'city_state_zip': 'count',
    'owner': 'count',
    'operator': 'count'
})

# Rename columns to match target schema
agg_df.rename(columns={
    'facid_int': 'facid',
    'capacity': 'capacity',
    'fac_name': 'fac_name',
    'fac_address': 'fac_address',
    'city_state_zip': 'city_state_zip',
    'owner': 'owner',
    'operator': 'operator'
}, inplace=True)

# Ensure fac_type is string, facid and other columns are integer
agg_df['fac_type'] = agg_df['fac_type'].astype(str)
agg_df['facid'] = agg_df['facid'].astype('Int64')
agg_df['capacity'] = agg_df['capacity'].astype('Int64')
agg_df['fac_name'] = agg_df['fac_name'].astype('Int64')
agg_df['fac_address'] = agg_df['fac_address'].astype('Int64')
agg_df['city_state_zip'] = agg_df['city_state_zip'].astype('Int64')
agg_df['owner'] = agg_df['owner'].astype('Int64')
agg_df['operator'] = agg_df['operator'].astype('Int64')

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)