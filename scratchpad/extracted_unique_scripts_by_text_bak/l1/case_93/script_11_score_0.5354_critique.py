import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_93/training_0.csv", index_col=0)
df0['bet'] = pd.to_numeric(df0['bet'], errors='coerce')
df0['win'] = pd.to_numeric(df0['win'], errors='coerce')
df0.to_csv("autopipeline-benchmarks/github-pipelines/length1_93/target_multisource_mcts.csv", index=False)