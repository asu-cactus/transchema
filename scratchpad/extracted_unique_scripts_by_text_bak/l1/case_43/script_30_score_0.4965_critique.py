import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df = df0.copy()

df['facid'] = pd.to_numeric(df['facid'], errors='coerce').astype('Int64')
df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce').astype('Int64')
df['fac_type'] = df['fac_type'].astype(str)
df['fac_name'] = df['fac_name'].astype(str)
df['fac_address'] = df['fac_address'].astype(str)
df['city_state_zip'] = df['city_state_zip'].astype(str)
df['owner'] = df['owner'].astype(str)
df['operator'] = df['operator'].astype(str)

grouped = df.groupby(['fac_type', 'facid'], dropna=False).agg(
    capacity=('capacity', 'count'),
    fac_name=('fac_name', 'count'),
    fac_address=('fac_address', 'count'),
    city_state_zip=('city_state_zip', 'count'),
    owner=('owner', 'count'),
    operator=('operator', 'count')
).reset_index()

grouped = grouped[['fac_type', 'facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)