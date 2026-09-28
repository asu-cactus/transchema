import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_73/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_73/training_1.csv", index_col=0)

grouped = df1.groupby("city", as_index=False)["fare"].mean()

result = pd.merge(df0, grouped, on="city", how="inner")

result = result[["city", "type", "fare"]]
result["fare"] = result["fare"].astype(float)
result["city"] = result["city"].astype(str)
result["type"] = result["type"].astype(str)

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_73/target_multisource_mcts.csv", index=False)