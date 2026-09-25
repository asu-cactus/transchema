import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_13/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_13/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_13/training_2.csv', index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

result = df.groupby(['sex', 'smoker'], as_index=False).agg({'tip_pct': 'mean'})

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_13/target_multisource_mcts.csv', index=False)