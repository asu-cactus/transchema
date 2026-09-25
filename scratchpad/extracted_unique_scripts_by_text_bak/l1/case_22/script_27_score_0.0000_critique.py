import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_22/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_22/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_22/training_2.csv', index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

df = df.astype({'condition': 'int64', 'click': 'int64'})

df = df.groupby('condition', as_index=False).agg({'click': 'sum'})

df.to_csv('autopipeline-benchmarks/github-pipelines/length1_22/target_multisource_mcts.csv', index=False)