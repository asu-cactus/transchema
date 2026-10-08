import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Group by fac_type and facid
grouped = df.groupby(['fac_type', 'facid'], dropna=False).agg({
    'capacity': 'sum',
    'fac_name': 'count',
    'fac_address': 'count',
    'city_state_zip': 'count',
    'owner': 'count',
    'operator': 'count'
}).reset_index()

# Rename columns to match target schema exactly
# fac_type is string, facid integer, others integer counts/sums
grouped['fac_type'] = grouped['fac_type'].astype(str)
grouped['facid'] = grouped['facid'].astype('Int64')
grouped['capacity'] = grouped['capacity'].astype('Int64')
grouped['fac_name'] = grouped['fac_name'].astype('Int64')
grouped['fac_address'] = grouped['fac_address'].astype('Int64')
grouped['city_state_zip'] = grouped['city_state_zip'].astype('Int64')
grouped['owner'] = grouped['owner'].astype('Int64')
grouped['operator'] = grouped['operator'].astype('Int64')

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)