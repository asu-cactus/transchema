import pandas as pd

# Read all source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_9.csv", index_col=0)

# UNION tables with the same schema
union_3457 = pd.concat([s3, s5, s6, s7], ignore_index=True)

# JOIN all tables on ROW_WID (inner join to keep only matching rows)
join_0 = pd.merge(union_3457, s0, on="ROW_WID", how="inner")
join_1 = pd.merge(join_0, s1, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s2, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s4, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s8, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s9, on="ROW_WID", how="inner")

# Group by ROW_WID and aggregate ARPU by mean
result = join_5.groupby("ROW_WID", dropna=False)["ARPU"].mean().reset_index()

# Output only ARPU column as per target schema
target = result[["ARPU"]].copy()
target["ARPU"] = target["ARPU"].astype(float)

target.to_csv("autopipeline-benchmarks/github-pipelines/length9_28/target_multisource_mcts.csv", index=False)