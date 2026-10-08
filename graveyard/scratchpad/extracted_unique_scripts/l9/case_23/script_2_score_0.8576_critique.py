import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_23/training_9.csv", index_col=0)

# UNION dimension tables with same schema
union_df = pd.concat([s2, s3, s6, s8], ignore_index=True)

# JOIN all aspect tables on ROW_WID using outer joins to avoid losing rows
join_1 = pd.merge(union_df, s0, on="ROW_WID", how="outer")
join_2 = pd.merge(join_1, s1, on="ROW_WID", how="outer")
join_3 = pd.merge(join_2, s4, on="ROW_WID", how="outer")
join_4 = pd.merge(join_3, s5, on="ROW_WID", how="outer")
join_5 = pd.merge(join_4, s7, on="ROW_WID", how="outer")
join_6 = pd.merge(join_5, s9, on="ROW_WID", how="outer")

# Filter rows where MONTHS_AGE is not null (target column)
result = join_6[join_6["MONTHS_AGE"].notnull()][["MONTHS_AGE"]].copy()

# Ensure MONTHS_AGE is float
result["MONTHS_AGE"] = result["MONTHS_AGE"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_23/target_multisource_mcts.csv", index=False)