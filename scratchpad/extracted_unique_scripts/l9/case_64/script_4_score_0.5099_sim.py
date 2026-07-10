import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_64/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_64/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_result = pd.concat(dfs, ignore_index=True)

grouped = union_result.groupby(['admit', 'prestige'], as_index=False).agg({'gre':'sum', 'gpa':'sum'})

grouped['admit'] = grouped['admit'].astype(int)
grouped['prestige'] = grouped['prestige'].astype(int)
grouped['gre'] = grouped['gre'].astype(int)
grouped['gpa'] = grouped['gpa'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_64/target_multisource_mcts.csv", index=False)