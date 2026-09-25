import pandas as pd

# Read dimension tables with same schema
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_4.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_8.csv", index_col=0)

# Union dimension tables
union_result = pd.concat([s2, s3, s4, s8], ignore_index=True)

# Read aspect tables
s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_1.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_7.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_26/training_9.csv", index_col=0)

# Join unioned dimension table with each aspect table on ROW_WID using left join to keep all dimension rows
joined = union_result.merge(s0, on="ROW_WID", how="left") \
                     .merge(s1, on="ROW_WID", how="left") \
                     .merge(s5, on="ROW_WID", how="left") \
                     .merge(s6, on="ROW_WID", how="left") \
                     .merge(s7, on="ROW_WID", how="left") \
                     .merge(s9, on="ROW_WID", how="left")

# Select only CANCEL_DT column as target schema
result = joined[["CANCEL_DT"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_26/target_multisource_mcts.csv", index=False)