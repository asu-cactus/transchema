import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_2.csv", index_col=0)
df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_38/training_3.csv", index_col=0)

union_0_1 = pd.concat([df0, df1], ignore_index=True)
union_2_3 = pd.concat([df2, df3], ignore_index=True)

merged = pd.merge(union_0_1, union_2_3, on="batsman", how="inner")

merged["batsman_runs_x"] = merged["batsman_runs"].astype(float)
merged["batsman_runs_y"] = merged["batsman_runs"].astype(float)
merged["batsman_runs"] = merged["batsman_runs"].astype(int)
merged["total_runs"] = merged["total_runs"].astype(int)

result = merged[["batsman", "batsman_runs_x", "total_runs", "batsman_runs_y", "batsman_runs"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_38/target_multisource_mcts.csv", index=False)