import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="fac_type", suffixes=('', '_dup'))

grouped = joined.groupby(['fac_type', 'facid'], as_index=False).agg({
    'capacity': 'sum',
    'fac_name': 'count',
    'fac_address': 'count',
    'city_state_zip': 'count',
    'owner': 'count',
    'operator': 'count'
})

grouped['fac_name'] = grouped['fac_name'].astype(int)
grouped['fac_address'] = grouped['fac_address'].astype(int)
grouped['city_state_zip'] = grouped['city_state_zip'].astype(int)
grouped['owner'] = grouped['owner'].astype(int)
grouped['operator'] = grouped['operator'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)