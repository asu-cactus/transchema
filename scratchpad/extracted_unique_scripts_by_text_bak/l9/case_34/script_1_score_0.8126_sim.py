import pandas as pd

s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

union_df = pd.concat([s2, s5, s6, s8], ignore_index=True)

merged = pd.merge(union_df, s9, on="ROW_WID", how="inner")

result = merged[["KEYWORDS_NUM"]].copy()
result["KEYWORDS_NUM"] = result["KEYWORDS_NUM"].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)