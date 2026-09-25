import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_100/training_2.csv", index_col=0)

# Join df0 and df1 on Country
df01 = pd.merge(df0, df1, how='inner', on='Country')

# Join the result with df2 on Country = Country Name
df012 = pd.merge(df01, df2, how='inner', left_on='Country', right_on='Country Name')

# Group by Rank and count Country occurrences (count of Country is count of rows per Rank)
result = df012.groupby('Rank', as_index=False).agg({'Country': 'count'})

# Rename count column to '0' as per target schema
result = result.rename(columns={'Country': '0'})

# Ensure types match target schema
result = result.astype({'Rank': int, '0': int})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_100/target_multisource_mcts.csv", index=False)