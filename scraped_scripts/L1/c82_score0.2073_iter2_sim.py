import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)

df = pd.concat([df0, df1], ignore_index=True)

df = df[['conservation_status', 'scientific_name']]

df['conservation_status'] = df['conservation_status'].astype(str)
df['scientific_name'] = pd.to_numeric(df['scientific_name'], errors='coerce').fillna(0).astype(int)

df.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)