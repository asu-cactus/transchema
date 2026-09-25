import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_0.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_2.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_1.csv", index_col=0)

union_result = pd.concat([df0, df2], ignore_index=True)

merged = pd.merge(union_result, df1, on="state", how="inner")

merged["year"] = merged["year"].astype(int)
merged["draw_sales"] = merged["draw_sales"].fillna(0).astype(int)
merged["full_state"] = merged["full_state"].astype(str)
merged["pop"] = merged["pop"].fillna(0).astype(int)

result = merged[["state", "year", "draw_sales", "full_state", "pop"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length5_6/target_multisource_mcts.csv", index=False)