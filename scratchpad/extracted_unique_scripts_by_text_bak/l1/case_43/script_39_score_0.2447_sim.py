import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df = df[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

df['fac_type'] = df['fac_type'].astype(str)
df['facid'] = pd.to_numeric(df['facid'], errors='coerce').astype('Int64')
df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce').astype('Int64')
df['fac_name'] = pd.to_numeric(df['fac_name'], errors='coerce').astype('Int64')
df['fac_address'] = pd.to_numeric(df['fac_address'], errors='coerce').astype('Int64')
df['city_state_zip'] = pd.to_numeric(df['city_state_zip'], errors='coerce').astype('Int64')
df['owner'] = pd.to_numeric(df['owner'], errors='coerce').astype('Int64')
df['operator'] = pd.to_numeric(df['operator'], errors='coerce').astype('Int64')

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)