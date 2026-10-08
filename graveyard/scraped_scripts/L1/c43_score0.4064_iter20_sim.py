import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

group_cols = ['facid', 'fac_type', 'capacity', 'fac_name', 'fac_address', 'city_state_zip']
agg_dict = {
    'owner': 'count',
    'operator': 'count'
}

result = df0.groupby(group_cols).agg(agg_dict).reset_index()

result = result.rename(columns={
    'owner': 'owner',
    'operator': 'operator'
})

result['fac_type'] = result['fac_type'].astype(str)
result['facid'] = pd.to_numeric(result['facid'], errors='coerce').fillna(0).astype(int)
result['capacity'] = pd.to_numeric(result['capacity'], errors='coerce').fillna(0).astype(int)
result['fac_name'] = result['fac_name'].astype(str)
result['fac_address'] = result['fac_address'].astype(str)
result['city_state_zip'] = result['city_state_zip'].astype(str)
result['owner'] = result['owner'].astype(int)
result['operator'] = result['operator'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)