import pandas as pd

# Read source table
df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Group by fac_type and facid, aggregate counts of other columns
agg_df = df0.groupby(['fac_type', 'facid'], as_index=False).agg({
    'capacity': 'count',
    'fac_name': 'count',
    'fac_address': 'count',
    'city_state_zip': 'count',
    'owner': 'count',
    'operator': 'count'
})

# Rename columns to match target schema exactly
agg_df = agg_df.rename(columns={
    'capacity': 'capacity',
    'fac_name': 'fac_name',
    'fac_address': 'fac_address',
    'city_state_zip': 'city_state_zip',
    'owner': 'owner',
    'operator': 'operator'
})

# Ensure types match target schema
agg_df['fac_type'] = agg_df['fac_type'].astype(str)
agg_df['facid'] = pd.to_numeric(agg_df['facid'], errors='coerce').astype('Int64')
agg_df['capacity'] = pd.to_numeric(agg_df['capacity'], errors='coerce').astype('Int64')
agg_df['fac_name'] = pd.to_numeric(agg_df['fac_name'], errors='coerce').astype('Int64')
agg_df['fac_address'] = pd.to_numeric(agg_df['fac_address'], errors='coerce').astype('Int64')
agg_df['city_state_zip'] = pd.to_numeric(agg_df['city_state_zip'], errors='coerce').astype('Int64')
agg_df['owner'] = pd.to_numeric(agg_df['owner'], errors='coerce').astype('Int64')
agg_df['operator'] = pd.to_numeric(agg_df['operator'], errors='coerce').astype('Int64')

# Write output
agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)