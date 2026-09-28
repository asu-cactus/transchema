import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

agg = df0.groupby(['facid', 'fac_type'], as_index=False).agg({
    'capacity': 'min',
    'fac_name': 'min',
    'fac_address': 'min',
    'city_state_zip': 'min',
    'owner': 'min',
    'operator': 'min'
})

agg['facid'] = agg['facid'].astype(int, errors='ignore')
agg['capacity'] = agg['capacity'].astype(int, errors='ignore')
agg['fac_name'] = agg['fac_name'].astype(int, errors='ignore')
agg['fac_address'] = agg['fac_address'].astype(int, errors='ignore')
agg['city_state_zip'] = agg['city_state_zip'].astype(int, errors='ignore')
agg['owner'] = agg['owner'].astype(int, errors='ignore')
agg['operator'] = agg['operator'].astype(int, errors='ignore')

agg = agg[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

agg.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)