import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_83/training_4.csv", index_col=0)

df_union = pd.concat([df0, df1, df2, df3, df4], ignore_index=True, sort=False)

result = df_union.groupby('Profit', dropna=False).size().reset_index(name='count')

# The target schema is only ['Profit': float], so we only keep 'Profit' column.
# The GROUP_BY : [Profit] operation implies grouping by Profit, but no aggregation specified.
# Since target examples only have Profit column, we just keep unique Profit values.

result = result[['Profit']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_83/target_multisource_mcts.csv", index=False)