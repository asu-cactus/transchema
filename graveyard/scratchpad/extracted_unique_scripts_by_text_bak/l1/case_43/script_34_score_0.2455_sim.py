import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df_joined = df0.merge(df0, on="facid", suffixes=('', '_dup'))

group_cols = ['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']
df_grouped = df_joined.groupby(group_cols, dropna=False).size().reset_index().drop(columns=0)

df_grouped['facid'] = pd.to_numeric(df_grouped['facid'], errors='coerce').astype('Int64')
df_grouped['capacity'] = pd.to_numeric(df_grouped['capacity'], errors='coerce').astype('Int64')
df_grouped['fac_name'] = df_grouped['fac_name'].astype(str)
df_grouped['fac_address'] = df_grouped['fac_address'].astype(str)
df_grouped['city_state_zip'] = df_grouped['city_state_zip'].astype(str)
df_grouped['owner'] = df_grouped['owner'].astype(str)
df_grouped['operator'] = df_grouped['operator'].astype(str)
df_grouped['fac_type'] = df_grouped['fac_type'].astype(str)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)