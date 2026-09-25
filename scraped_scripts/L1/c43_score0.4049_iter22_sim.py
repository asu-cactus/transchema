import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df_joined = df0.merge(df0, on="facid", suffixes=('', '_dup'))

id_vars = ['facid', 'fac_type', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']
value_vars = [col for col in df_joined.columns if col not in id_vars]

df_unpivot = pd.melt(df_joined, id_vars=['facid'], value_vars=value_vars, var_name='fac_type', value_name='value')

df_unpivot['fac_type'] = df_unpivot['fac_type'].str.replace('_dup', '', regex=False)

df_unpivot = df_unpivot.rename(columns={'value': 'fac_name'})

df_unpivot['capacity'] = pd.to_numeric(df_unpivot['fac_name'], errors='coerce').fillna(0).astype(int)
df_unpivot['fac_name'] = df_unpivot['capacity']
df_unpivot['fac_address'] = df_unpivot['capacity']
df_unpivot['city_state_zip'] = df_unpivot['capacity']
df_unpivot['owner'] = df_unpivot['capacity']
df_unpivot['operator'] = df_unpivot['capacity']

df_unpivot = df_unpivot[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

df_unpivot['capacity'] = df_unpivot['capacity'].astype(int)
df_unpivot['fac_name'] = df_unpivot['fac_name'].astype(int)
df_unpivot['fac_address'] = df_unpivot['fac_address'].astype(int)
df_unpivot['city_state_zip'] = df_unpivot['city_state_zip'].astype(int)
df_unpivot['owner'] = df_unpivot['owner'].astype(int)
df_unpivot['operator'] = df_unpivot['operator'].astype(int)

df_unpivot.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)