import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_5/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_5/training_10.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)
df_grouped = df_all.groupby(['code', 'name'], as_index=False).size()
df_grouped = df_grouped[['code', 'name']]
df_grouped['code'] = df_grouped['code'].astype(int)
df_grouped['name'] = df_grouped['name'].astype(str)
df_grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_5/target_multisource_mcts.csv", index=False)