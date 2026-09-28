import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_38/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_38/training_1.csv", index_col=0)

grouped = df1.groupby('city', as_index=False).agg({'fare':'mean'})

joined = pd.merge(df0, grouped, on='city', how='inner')

result = joined.groupby('type', as_index=False).agg({'fare':'sum'})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_38/target_multisource_mcts.csv", index=False)