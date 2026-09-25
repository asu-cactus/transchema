import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_76/training_1.csv", index_col=0)

# Join on city to get type from df0 and fare from df1
joined = pd.merge(df0[['city', 'type']], df1[['city', 'fare']], on='city', how='inner')

# Group by city and type, aggregate mean fare
result = joined.groupby(['city', 'type'], as_index=False).agg({'fare': 'mean'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_76/target_multisource_mcts.csv", index=False)