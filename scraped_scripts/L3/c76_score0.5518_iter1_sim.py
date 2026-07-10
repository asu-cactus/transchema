import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_76/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_76/training_1.csv", index_col=0)

merged = pd.merge(df0, df1[['city', 'fare']], on='city')

result = merged[['city', 'type', 'fare']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_76/target_multisource_mcts.csv", index=False)