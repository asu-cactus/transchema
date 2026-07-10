import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg_df = df0.groupby(['fac_type', 'facid']).agg({
    'capacity': 'sum',
    'fac_name': 'count',
    'fac_address': 'count',
    'city_state_zip': 'count',
    'owner': 'count',
    'operator': 'count'
}).reset_index()

# Rename columns to match target schema exactly
agg_df = agg_df.rename(columns={
    'capacity': 'capacity',
    'fac_name': 'fac_name',
    'fac_address': 'fac_address',
    'city_state_zip': 'city_state_zip',
    'owner': 'owner',
    'operator': 'operator'
})

# Ensure correct types
agg_df['fac_type'] = agg_df['fac_type'].astype(str)
agg_df['facid'] = agg_df['facid'].astype(int)
agg_df['capacity'] = agg_df['capacity'].astype(int)
agg_df['fac_name'] = agg_df['fac_name'].astype(int)
agg_df['fac_address'] = agg_df['fac_address'].astype(int)
agg_df['city_state_zip'] = agg_df['city_state_zip'].astype(int)
agg_df['owner'] = agg_df['owner'].astype(int)
agg_df['operator'] = agg_df['operator'].astype(int)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)