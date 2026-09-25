import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_34/training_9.csv", index_col=0)

union_result = pd.concat([s2, s5, s6, s8], ignore_index=True)

dfs_to_join = [s9, s0, s1, s3, s4, s7, union_result]

df_merged = dfs_to_join[0]
for df in dfs_to_join[1:]:
    df_merged = df_merged.merge(df, on="ROW_WID", how="inner")

result = df_merged.groupby("KEYWORDS_NUM", as_index=False).size()
result = result.rename(columns={"size": "KEYWORDS_NUM"})
result = result[["KEYWORDS_NUM"]]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_34/target_multisource_mcts.csv", index=False)