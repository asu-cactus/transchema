import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_71/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_71/training_1.csv", index_col=0)

grouped = df1.groupby("city", as_index=False)["fare"].mean()

merged = pd.merge(df0, grouped, on="city", how="inner")

result = merged[["city", "type", "fare"]]
result.to_csv("autopipeline-benchmarks/github-pipelines/length3_71/target_multisource_mcts.csv", index=False)