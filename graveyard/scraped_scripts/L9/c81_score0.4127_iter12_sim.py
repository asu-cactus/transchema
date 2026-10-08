import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_81/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_81/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)

grouped = union_df.groupby(['admit', 'prestige'], as_index=False).agg({
    'admit': 'sum',
    'gre': 'min',
    'gpa': 'max'
})

grouped = grouped.rename(columns={'admit': 'admit', 'gre': 'gre', 'gpa': 'gpa', 'prestige': 'prestige'})

grouped['admit'] = grouped['admit'].astype(int)
grouped['gre'] = grouped['gre'].astype(int)
grouped['prestige'] = grouped['prestige'].astype(int)
grouped['gpa'] = grouped['gpa'].astype(float)

grouped.to_csv("autopipeline-benchmarks/github-pipelines/length9_81/target_multisource_mcts.csv", index=False)