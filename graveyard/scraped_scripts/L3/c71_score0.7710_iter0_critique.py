import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_71/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_71/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

grouped = merged.groupby(["city", "type"], as_index=False)["fare"].mean()

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length3_71/target_multisource_mcts.csv", index=False)