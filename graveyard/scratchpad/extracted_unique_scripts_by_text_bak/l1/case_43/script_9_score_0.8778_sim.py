import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

pivoted = df0.groupby('fac_type').agg({
    'facid': 'count',
    'capacity': 'count',
    'fac_name': 'count',
    'fac_address': 'count',
    'city_state_zip': 'count',
    'owner': 'count',
    'operator': 'count'
}).reset_index()

pivoted = pivoted.rename(columns={
    'facid': 'facid',
    'capacity': 'capacity',
    'fac_name': 'fac_name',
    'fac_address': 'fac_address',
    'city_state_zip': 'city_state_zip',
    'owner': 'owner',
    'operator': 'operator'
})

pivoted = pivoted.astype({
    'fac_type': str,
    'facid': int,
    'capacity': int,
    'fac_name': int,
    'fac_address': int,
    'city_state_zip': int,
    'owner': int,
    'operator': int
})

pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)