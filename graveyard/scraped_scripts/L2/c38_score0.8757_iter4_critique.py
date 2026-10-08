import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_38/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_38/training_1.csv", index_col=0)

merged = pd.merge(df0, df1, on="city", how="inner")

urban_rows = merged[merged["type"] == "Urban"]

total_fare = urban_rows["fare"].sum()

result = pd.DataFrame({"type": ["Urban"], "fare": [float(total_fare)]})

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_38/target_multisource_mcts.csv", index=False)