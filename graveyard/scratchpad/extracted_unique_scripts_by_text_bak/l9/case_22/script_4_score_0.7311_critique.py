import pandas as pd

# Load source tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_22/training_9.csv", index_col=0)

# UNION the dimension tables with the same schema
unioned_dim = pd.concat([s3, s4, s7, s8], ignore_index=True)

# JOIN all tables on ROW_WID
joined = unioned_dim.merge(s0, on="ROW_WID", how="inner") \
                    .merge(s1, on="ROW_WID", how="inner") \
                    .merge(s2, on="ROW_WID", how="inner") \
                    .merge(s5, on="ROW_WID", how="inner") \
                    .merge(s6, on="ROW_WID", how="inner") \
                    .merge(s9, on="ROW_WID", how="inner")

# Select the target column
target_df = joined[["INBOUND_CALLS_NUM"]].copy()
target_df["INBOUND_CALLS_NUM"] = target_df["INBOUND_CALLS_NUM"].astype("Int64")

# Write output
target_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_22/target_multisource_mcts.csv", index=False)