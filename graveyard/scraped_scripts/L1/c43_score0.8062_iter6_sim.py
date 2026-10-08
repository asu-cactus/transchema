import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="fac_type", suffixes=('_left', '_right'))

grouped = joined.groupby('fac_type').agg({
    'facid_left': 'count',
    'capacity_left': 'count',
    'fac_name_left': 'count',
    'fac_address_left': 'count',
    'city_state_zip_left': 'count',
    'owner_left': 'count',
    'operator_left': 'count'
}).reset_index()

grouped.columns = ['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']

grouped['facid'] = grouped['facid'].astype(int)
grouped['capacity'] = grouped['capacity'].astype(int)
grouped['fac_name'] = grouped['fac_name'].astype(int)
grouped['fac_address'] = grouped['fac_address'].astype(int)
grouped['city_state_zip'] = grouped['city_state_zip'].astype(int)
grouped['owner'] = grouped['owner'].astype(int)
grouped['operator'] = grouped['operator'].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)