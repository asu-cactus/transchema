import pandas as pd

df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_3.csv", index_col=0)
df6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_6.csv", index_col=0)
df8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_8.csv", index_col=0)

df_union = pd.concat([df2, df3, df6, df8], ignore_index=True)

result = df_union[['MONTHS_AGE']].groupby('MONTHS_AGE', as_index=False).size()

result = result.rename(columns={'size': 'count'})

# The target schema only requires MONTHS_AGE column, so we keep unique MONTHS_AGE values
# The target examples show only MONTHS_AGE column, so we drop the count column
result = result[['MONTHS_AGE']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts.csv", index=False)