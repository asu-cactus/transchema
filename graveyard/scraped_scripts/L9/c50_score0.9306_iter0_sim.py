import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_50/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_50/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_grouped = df_all.groupby('emp_length', as_index=False).size()
df_grouped.rename(columns={'size': 'emp_length'}, inplace=True)
df_grouped['emp_length'] = df_grouped['emp_length'].astype(int)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_50/target_multisource_mcts.csv", index=False)