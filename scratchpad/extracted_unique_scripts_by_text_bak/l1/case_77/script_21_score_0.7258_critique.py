import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)

df0['fac_type'] = df0['fac_type'].astype(str)
df0['capacity'] = pd.to_numeric(df0['capacity'], errors='coerce').fillna(0).astype(int)

result = df0.groupby('fac_type', as_index=False).agg({'capacity': 'sum'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)