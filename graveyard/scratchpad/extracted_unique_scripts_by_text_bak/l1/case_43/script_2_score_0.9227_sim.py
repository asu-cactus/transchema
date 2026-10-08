import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_43/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

agg_dict = {
    'facid': 'max',
    'capacity': 'max',
    'fac_name': 'max',
    'fac_address': 'max',
    'city_state_zip': 'max',
    'owner': 'max',
    'operator': 'max'
}

df_grouped = df.groupby('fac_type', as_index=False).agg(agg_dict)

for col in ['facid', 'capacity', 'fac_name', 'fac_address', 'city_state_zip', 'owner', 'operator']:
    df_grouped[col] = pd.to_numeric(df_grouped[col], errors='coerce').fillna(0).astype(int)

df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length1_43/target_multisource_mcts.csv", index=False)