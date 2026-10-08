import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

joined = pd.merge(df0, df0, on="facid", suffixes=('_left', '_right'))

unioned = pd.concat([df0, df0], ignore_index=True)

result = unioned.copy()

result['fac_type'] = result['fac_type'].astype(str)
result['facid'] = pd.to_numeric(result['facid'], errors='coerce').astype('Int64')
result['capacity'] = pd.to_numeric(result['capacity'], errors='coerce').astype('Int64')
result['fac_name'] = pd.to_numeric(result['fac_name'], errors='coerce').astype('Int64')
result['fac_address'] = pd.to_numeric(result['fac_address'], errors='coerce').astype('Int64')
result['city_state_zip'] = pd.to_numeric(result['city_state_zip'], errors='coerce').astype('Int64')
result['owner'] = pd.to_numeric(result['owner'], errors='coerce').astype('Int64')
result['operator'] = pd.to_numeric(result['operator'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)