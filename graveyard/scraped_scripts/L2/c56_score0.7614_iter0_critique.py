import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_56/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_56/training_1.csv", index_col=0)

joined = pd.merge(df0, df1, on="city", how="inner")

result = joined.groupby("city", as_index=False)["fare"].sum()

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_56/target_multisource_mcts.csv", index=False)