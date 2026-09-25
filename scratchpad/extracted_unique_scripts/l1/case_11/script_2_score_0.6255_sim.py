import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_11/training_0.csv", index_col=0)
df = df0[['sex', 'births']].copy()
df['births'] = df['births'].astype(int)
df.to_csv("autopipeline-benchmarks/github-pipelines/length1_11/target_multisource_mcts.csv", index=False)