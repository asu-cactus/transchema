import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_82/training_0.csv", index_col=0)
df = df0[['conservation_status', 'scientific_name']].copy()
df['scientific_name'] = pd.to_numeric(df['scientific_name'], errors='coerce')
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts.csv", index=False)