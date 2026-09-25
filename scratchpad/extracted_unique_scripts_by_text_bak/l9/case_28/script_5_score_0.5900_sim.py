import pandas as pd

s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_3.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_7.csv", index_col=0)

union_df = pd.concat([s3, s5, s6, s7], ignore_index=True)

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_0.csv", index_col=0)
join_1 = pd.merge(union_df, s0, on="ROW_WID", how="inner")

s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_1.csv", index_col=0)
join_2 = pd.merge(join_1, s1, on="ROW_WID", how="inner")

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_2.csv", index_col=0)
join_3 = pd.merge(join_2, s2, on="ROW_WID", how="inner")

s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_4.csv", index_col=0)
join_4 = pd.merge(join_3, s4, on="ROW_WID", how="inner")

s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_8.csv", index_col=0)
join_5 = pd.merge(join_4, s8, on="ROW_WID", how="inner")

s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_28/training_9.csv", index_col=0)
join_6 = pd.merge(join_5, s9, on="ROW_WID", how="inner")

result = join_6.groupby("ARPU", as_index=False).size().rename(columns={"size": "count"})

# The target schema only requires 'ARPU' column, so we keep only ARPU column.
final_result = result[["ARPU"]]

final_result.to_csv("autopipeline-benchmarks/github-pipelines/length9_28/target_multisource_mcts.csv", index=False)