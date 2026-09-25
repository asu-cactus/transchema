import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df = df0.copy()

df['facid'] = pd.to_numeric(df['facid'], errors='coerce')
df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')
df['fac_name'] = df['fac_name'].astype(str).apply(lambda x: len(x))
df['fac_address'] = df['fac_address'].astype(str).apply(lambda x: len(x))
df['city_state_zip'] = df['city_state_zip'].astype(str).apply(lambda x: len(x))
df['owner'] = df['owner'].astype(str).apply(lambda x: len(x))
df['operator'] = df['operator'].astype(str).apply(lambda x: len(x))

result = df.groupby('fac_type', as_index=False).agg({
    'facid': 'max',
    'capacity': 'max',
    'fac_name': 'max',
    'fac_address': 'max',
    'city_state_zip': 'max',
    'owner': 'max',
    'operator': 'max'
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)