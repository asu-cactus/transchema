import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df = df0.copy()

df['facid'] = pd.to_numeric(df['facid'], errors='coerce')
df = df.dropna(subset=['facid'])
df['facid'] = df['facid'].astype(int)

df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')

df['fac_name'] = df['fac_name'].astype(str).apply(len)
df['fac_address'] = df['fac_address'].astype(str).apply(len)
df['city_state_zip'] = df['city_state_zip'].astype(str).apply(len)
df['owner'] = df['owner'].astype(str).apply(len)
df['operator'] = df['operator'].astype(str).apply(len)

result = df.groupby(['fac_type', 'facid'], as_index=False).agg({
    'capacity': 'max',
    'fac_name': 'max',
    'fac_address': 'max',
    'city_state_zip': 'max',
    'owner': 'max',
    'operator': 'max'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)