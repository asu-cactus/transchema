import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_88/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df['admit'] = df['admit'].astype(int)
df['gre'] = df['gre'].astype(int)
df['prestige'] = df['prestige'].astype(int)
df['gpa'] = df['gpa'].astype(float)

df.to_csv("autopipeline-benchmarks/github-pipelines/length9_88/target_multisource_mcts.csv", index=False)