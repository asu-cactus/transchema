import pandas as pd

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_3.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_7.csv", index_col=0)

union_df = pd.concat([s3, s5, s6, s7], ignore_index=True)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_2.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_4.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_9.csv", index_col=0)

df = union_df.merge(s0, on="ROW_WID", how="inner")
df = df.merge(s1, on="ROW_WID", how="inner")
df = df.merge(s2, on="ROW_WID", how="inner")
df = df.merge(s4, on="ROW_WID", how="inner")
df = df.merge(s8, on="ROW_WID", how="inner")
df = df.merge(s9, on="ROW_WID", how="inner")

result = df.groupby("ARPU", as_index=False).size().rename(columns={"size": "count"})

# The target schema is only ['ARPU'], so we keep only ARPU column
result = result[["ARPU"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_28/target_multisource_mcts.csv", index=False)