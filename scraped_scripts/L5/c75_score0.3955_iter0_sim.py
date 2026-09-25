import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_75/training_4.csv", index_col=0)

result = df0.groupby('Profit', as_index=False).size()
# The above line groups by Profit and counts occurrences, but target schema only needs Profit column.
# Since target schema is only ['Profit'] and target examples show distinct Profit values,
# we just need unique Profit values from df0.

result = pd.DataFrame({'Profit': df0['Profit'].unique()})
result = result.sort_values('Profit').reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_75/target_multisource_mcts.csv", index=False)