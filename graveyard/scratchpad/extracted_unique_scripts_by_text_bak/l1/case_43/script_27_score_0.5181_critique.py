import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

# Group by fac_type and facid
agg_df = df0.groupby(['fac_type', 'facid']).agg({
    'capacity': 'sum',
    'fac_name': pd.Series.nunique,
    'fac_address': pd.Series.nunique,
    'city_state_zip': pd.Series.nunique,
    'owner': pd.Series.nunique,
    'operator': pd.Series.nunique
}).reset_index()

# Rename columns to match target schema
agg_df = agg_df.rename(columns={
    'fac_type': 'fac_type',
    'facid': 'facid',
    'capacity': 'capacity',
    'fac_name': 'fac_name',
    'fac_address': 'fac_address',
    'city_state_zip': 'city_state_zip',
    'owner': 'owner',
    'operator': 'operator'
})

# Ensure correct dtypes
agg_df['facid'] = agg_df['facid'].astype(int, errors='ignore')
agg_df['capacity'] = agg_df['capacity'].astype(int, errors='ignore')
agg_df['fac_name'] = agg_df['fac_name'].astype(int, errors='ignore')
agg_df['fac_address'] = agg_df['fac_address'].astype(int, errors='ignore')
agg_df['city_state_zip'] = agg_df['city_state_zip'].astype(int, errors='ignore')
agg_df['owner'] = agg_df['owner'].astype(int, errors='ignore')
agg_df['operator'] = agg_df['operator'].astype(int, errors='ignore')

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)