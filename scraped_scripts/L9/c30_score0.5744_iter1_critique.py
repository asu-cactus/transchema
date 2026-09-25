import pandas as pd

# Read the four large tables with same schema
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)

# UNION these four tables
union_result = pd.concat([s3, s4, s5, s7], ignore_index=True)

# Aggregate ARPU by mean per ROW_WID to remove duplicates
union_agg = union_result.groupby("ROW_WID", as_index=False).agg({"ARPU": "mean"})

# Read other source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_2.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_6.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_9.csv", index_col=0)

# Join all tables on ROW_WID
join_0 = pd.merge(union_agg, s0, on="ROW_WID", how="inner")
join_1 = pd.merge(join_0, s1, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s2, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s6, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s8, on="ROW_WID", how="inner")
final_join = pd.merge(join_4, s9, on="ROW_WID", how="inner")

# Group by ROW_WID and aggregate ARPU by mean (to ensure unique rows)
result = final_join.groupby("ROW_WID", as_index=False).agg({"ARPU": "mean"})

# Project ARPU only
result = result[["ARPU"]]

# Ensure ARPU is float type
result["ARPU"] = result["ARPU"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv", index=False)