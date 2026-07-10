import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_82/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_82/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

# Ensure columns are in the correct order and types match target schema
df_all = df_all[['admit', 'gre', 'gpa', 'prestige']]

df_all['admit'] = df_all['admit'].astype(int)
df_all['gre'] = df_all['gre'].astype(int)
df_all['gpa'] = df_all['gpa'].astype(float)
df_all['prestige'] = df_all['prestige'].astype(int)

df_all.to_csv("autopipeline-benchmarks/github-pipelines/length9_82/target_multisource_mcts.csv", index=False)