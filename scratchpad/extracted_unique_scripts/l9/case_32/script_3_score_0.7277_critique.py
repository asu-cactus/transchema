import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_32/training_9.csv", index_col=0)

# Union sources 5,6,7,8 (dimension tables with same schema)
unioned_dim = pd.concat([s5, s6, s7, s8], ignore_index=True)

# Group unioned_dim by ROW_WID to remove duplicates, aggregate by first (to keep one row per ROW_WID)
unioned_dim_unique = unioned_dim.groupby("ROW_WID", as_index=False).first()

# Join metric tables on ROW_WID to get all *_NUM columns in one wide table
joined_metrics = s0.merge(s1, on="ROW_WID", how="inner") \
                   .merge(s2, on="ROW_WID", how="inner") \
                   .merge(s3, on="ROW_WID", how="inner") \
                   .merge(s4, on="ROW_WID", how="inner") \
                   .merge(s9, on="ROW_WID", how="inner")

# Join the unique dimension table with the joined metrics on ROW_WID
final_join = unioned_dim_unique.merge(joined_metrics, on="ROW_WID", how="inner")

# Select only VISITS_NUM column as per target schema
result = final_join[["VISITS_NUM"]]

# Convert VISITS_NUM to integer type matching target schema
result["VISITS_NUM"] = result["VISITS_NUM"].astype("Int64")

# Save to target CSV
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_32/target_multisource_mcts.csv", index=False)