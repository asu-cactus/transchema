import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_56/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_9.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_10.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_11.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_12.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_13.csv",
    "autopipeline-benchmarks/github-pipelines/length9_56/training_14.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df_all = pd.concat(dfs, ignore_index=True)

# The target schema is ['last_pymnt_d': integer], so ensure the column is integer type
df_all['last_pymnt_d'] = df_all['last_pymnt_d'].astype(int)

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_56/target_multisource_mcts.csv", index=False)