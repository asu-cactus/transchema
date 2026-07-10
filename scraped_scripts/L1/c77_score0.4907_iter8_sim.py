import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_77/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)
df = df[['fac_type', 'capacity']]
df['fac_type'] = df['fac_type'].astype(str)
df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_77/target_multisource_mcts.csv", index=False)