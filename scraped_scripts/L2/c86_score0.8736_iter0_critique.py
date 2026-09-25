import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_86/training_1.csv", index_col=0)

# Inner join on 'fname' to keep only matching rows
joined = pd.merge(df0, df1[['fname']], on='fname', how='inner')

# Group by 'fname' and count rows from df0 (or joined)
result = joined.groupby('fname').size().reset_index(name='row_count')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_86/target_multisource_mcts.csv", index=False)