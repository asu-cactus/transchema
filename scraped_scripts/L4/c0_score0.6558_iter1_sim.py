import pandas as pd

df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_0/training_3.csv", index_col=0)
result = df3[['des_territ']].dropna(subset=['des_territ']).drop_duplicates().reset_index(drop=True)
result.to_csv("autopipeline-benchmarks/github-pipelines/length4_0/target_multisource_mcts.csv", index=False)