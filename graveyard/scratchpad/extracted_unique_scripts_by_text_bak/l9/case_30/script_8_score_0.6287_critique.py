import pandas as pd

# Read dimension tables
dim3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_3.csv", index_col=0)
dim4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_4.csv", index_col=0)
dim5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_5.csv", index_col=0)
dim7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_7.csv", index_col=0)

# Union dimension tables
dim_all = pd.concat([dim3, dim4, dim5, dim7], ignore_index=True)

# Read aspect tables
source0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_0.csv", index_col=0)
source1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_1.csv", index_col=0)
source2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_2.csv", index_col=0)
source6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_6.csv", index_col=0)
source8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_8.csv", index_col=0)
source9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_30/training_9.csv", index_col=0)

# Join dimension with each aspect table on ROW_WID
df = dim_all.merge(source0, on="ROW_WID", how="inner")
df = df.merge(source1, on="ROW_WID", how="inner")
df = df.merge(source2, on="ROW_WID", how="inner")
df = df.merge(source6, on="ROW_WID", how="inner")
df = df.merge(source8, on="ROW_WID", how="inner")
df = df.merge(source9, on="ROW_WID", how="inner")

# Aggregate mean ARPU (no group by columns)
# Since ROW_WID is unique key, just take mean ARPU per ROW_WID (which is just ARPU itself)
# But to be safe, group by ROW_WID and take mean ARPU
result = df.groupby("ROW_WID", as_index=False).agg({"ARPU": "mean"})

# Output only ARPU column as per target schema
result = result[["ARPU"]]

# Write output
result.to_csv("autopipeline-benchmarks/github-pipelines/length9_30/target_multisource_mcts.csv", index=False)