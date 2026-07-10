import pandas as pd
import numpy as np

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

grouped = df_all.groupby('prestige').agg({
    'gre': 'sum',
    'admit': 'mean',
    'gpa': 'min'
}).reset_index()

grouped['admit'] = grouped['admit'].round().astype(int)
grouped['gre'] = grouped['gre'].astype(int)
grouped['gpa'] = grouped['gpa'].astype(float)
grouped['prestige'] = grouped['prestige'].astype(int)

grouped = grouped[['admit', 'gre', 'gpa', 'prestige']]

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_82/target_multisource_mcts.csv", index=False)