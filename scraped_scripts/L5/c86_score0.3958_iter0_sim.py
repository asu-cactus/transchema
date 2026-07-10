import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_3.csv", index_col=0)
df4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_86/training_4.csv", index_col=0)

result = df2.groupby('Profit', as_index=False).size().rename(columns={'size':'count'})

# The target schema is just ['Profit': integer], and the target examples show unique Profit values.
# So we just need the distinct Profit values as integers.
# The groupby above counts occurrences but target only needs Profit column.
# So we take unique Profit values and convert to int.

result = pd.DataFrame({'Profit': df2['Profit'].dropna().astype(int).unique()})
result = result.sort_values('Profit').reset_index(drop=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_86/target_multisource_mcts.csv", index=False)