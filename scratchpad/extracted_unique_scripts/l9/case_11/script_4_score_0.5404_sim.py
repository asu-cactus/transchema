import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_11/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_11/training_9.csv",
]

dfs = []
for path in paths:
    df = pd.read_csv(path, index_col=0)
    dfs.append(df)

from functools import reduce

df_merged = reduce(lambda left, right: pd.merge(left, right, on='2012-12-05', how='outer'), dfs)

df_merged['2012-12-05'] = df_merged['2012-12-05'].astype(str)
df_merged['301.0'] = pd.to_numeric(df_merged['301.0'], errors='coerce').astype('Int64')
df_merged['0.0075805085'] = pd.to_numeric(df_merged['0.0075805085'], errors='coerce').astype(float)
df_merged['0.0179'] = pd.to_numeric(df_merged['0.0179'], errors='coerce').astype(float)
df_merged['6.9'] = pd.to_numeric(df_merged['6.9'], errors='coerce').astype(float)
df_merged['0.17657143'] = pd.to_numeric(df_merged['0.17657143'], errors='coerce').astype(float)
df_merged['20.3333'] = pd.to_numeric(df_merged['20.3333'], errors='coerce').astype(float)
df_merged['0.016157143'] = pd.to_numeric(df_merged['0.016157143'], errors='coerce').astype(float)
df_merged['242.364'] = pd.to_numeric(df_merged['242.364'], errors='coerce').astype(float)
df_merged['0.1646'] = pd.to_numeric(df_merged['0.1646'], errors='coerce').astype(float)
df_merged['0.7268'] = pd.to_numeric(df_merged['0.7268'], errors='coerce').astype(float)

df_merged = df_merged[['2012-12-05', '301.0', '0.0075805085', '0.0179', '6.9', '0.17657143', '20.3333', '0.016157143', '242.364', '0.1646', '0.7268']]

df_merged.to_csv("autopipeline-benchmarks/github-pipelines/length9_11/target_multisource_mcts.csv", index=False)