import pandas as pd

s0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_0.csv", index_col=0)
s1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_1.csv", index_col=0)
s2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_2.csv", index_col=0)
s3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_3.csv", index_col=0)
s4 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_4.csv", index_col=0)
s5 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_5.csv", index_col=0)
s6 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_6.csv", index_col=0)
s7 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_7.csv", index_col=0)
s8 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_8.csv", index_col=0)
s9 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_9.csv", index_col=0)
s10 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_12/training_10.csv", index_col=0)

dfs = [s0, s6, s8, s7, s9, s10, s5, s3, s4, s2, s1]

from functools import reduce
df_merged = reduce(lambda left, right: pd.merge(left, right, on='2012-12-05', how='outer'), dfs)

df_merged['2012-12-05'] = df_merged['2012-12-05'].astype(str)
df_merged['301.0'] = pd.to_numeric(df_merged['301.0'], errors='coerce').astype('Int64')

float_cols = ['0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268', '0.4332']
for col in float_cols:
    df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce').astype(float)

df_merged = df_merged[['2012-12-05', '301.0', '0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268', '0.4332']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length9_12/target_multisource_mcts.csv", index=False)