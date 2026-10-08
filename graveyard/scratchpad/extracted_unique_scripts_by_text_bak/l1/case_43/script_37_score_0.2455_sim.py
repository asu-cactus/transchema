import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df0['facid'] = pd.to_numeric(df0['facid'], errors='coerce').astype('Int64')
df0['capacity'] = pd.to_numeric(df0['capacity'], errors='coerce').astype('Int64')
df0['fac_name'] = pd.to_numeric(df0['fac_name'], errors='coerce').astype('Int64')
df0['fac_address'] = pd.to_numeric(df0['fac_address'], errors='coerce').astype('Int64')
df0['city_state_zip'] = pd.to_numeric(df0['city_state_zip'], errors='coerce').astype('Int64')
df0['owner'] = pd.to_numeric(df0['owner'], errors='coerce').astype('Int64')
df0['operator'] = pd.to_numeric(df0['operator'], errors='coerce').astype('Int64')

df0 = df0[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)