import pandas as pd

source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length5_6/training_2.csv", index_col=0)

union_result = pd.concat([source0, source2], ignore_index=True)

merged = pd.merge(union_result, source1, on="state", how="inner")

merged["year"] = merged["year"].astype(int)
merged["draw_sales"] = merged["draw_sales"].fillna(0).astype(int)
merged["full_state"] = merged["full_state"]
merged["pop"] = merged["pop"].fillna(0).astype(int)

grouped = merged.groupby(["state", "year", "full_state", "pop"], as_index=False).agg({"draw_sales": "sum"})

grouped["draw_sales"] = grouped["draw_sales"].astype(int)
grouped["pop"] = grouped["pop"].astype(int)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length5_6/target_multisource_mcts.csv", index=False)