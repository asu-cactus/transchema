import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df0['facid'] = pd.to_numeric(df0['facid'], errors='coerce')
df0['capacity'] = pd.to_numeric(df0['capacity'], errors='coerce')
df0['fac_name'] = df0['fac_name'].astype('string')
df0['fac_address'] = df0['fac_address'].astype('string')
df0['city_state_zip'] = df0['city_state_zip'].astype('string')
df0['owner'] = df0['owner'].astype('string')
df0['operator'] = df0['operator'].astype('string')
df0['fac_type'] = df0['fac_type'].astype('string')

df0['fac_name'] = df0['fac_name'].str.len()
df0['fac_address'] = df0['fac_address'].str.len()
df0['city_state_zip'] = df0['city_state_zip'].str.len()
df0['owner'] = df0['owner'].str.len()
df0['operator'] = df0['operator'].str.len()

df0 = df0[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)