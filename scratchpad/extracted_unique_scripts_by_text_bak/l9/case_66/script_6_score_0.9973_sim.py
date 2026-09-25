import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_66/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_66/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_0_1_2_4_5_6_7_8_9 = pd.concat(dfs, ignore_index=True)

df3 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length9_66/training_3.csv", index_col=0)

Target9_66 = pd.concat([union_0_1_2_4_5_6_7_8_9, df3], ignore_index=True)

Target9_66 = Target9_66.astype({
    'admit': 'int64',
    'gre': 'int64',
    'gpa': 'float64',
    'prestige': 'int64'
})

Target9_66.to_csv("autopipeline-benchmarks/github-pipelines/length9_66/target_multisource_mcts.csv", index=False)