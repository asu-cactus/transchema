import pandas as pd

# Read all sources
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_9.csv", index_col=0)

# UNION dimension tables with same schema
unioned_dim = pd.concat([s3, s4, s5, s7], ignore_index=True)

# JOIN unioned_dim with all other aspect tables on ROW_WID using inner joins
join_1 = pd.merge(unioned_dim, s0, on="ROW_WID", how="inner")
join_2 = pd.merge(join_1, s1, on="ROW_WID", how="inner")
join_3 = pd.merge(join_2, s2, on="ROW_WID", how="inner")
join_4 = pd.merge(join_3, s6, on="ROW_WID", how="inner")
join_5 = pd.merge(join_4, s8, on="ROW_WID", how="inner")
join_6 = pd.merge(join_5, s9, on="ROW_WID", how="inner")

# Project only ARPU column as per target schema
result = join_6[["ARPU"]].copy()

# Ensure ARPU is float type
result["ARPU"] = result["ARPU"].astype(float)

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv", index=False)