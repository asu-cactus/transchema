import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_63/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_63/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_63/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_63/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_63/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_63/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_63/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_63/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_63/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_63/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg = df_all.groupby(['admit', 'prestige'], as_index=False).agg({
    'admit': 'sum',
    'gre': 'min',
    'gpa': 'max'
})

agg = agg.rename(columns={'admit': 'admit', 'gre': 'gre', 'gpa': 'gpa', 'prestige': 'prestige'})

agg['admit'] = agg['admit'].astype(int)
agg['gre'] = agg['gre'].astype(int)
agg['prestige'] = agg['prestige'].astype(int)
agg['gpa'] = agg['gpa'].astype(float)

agg.to_csv("autopipeline-benchmarks/github-pipelines/length9_63/target_multisource_mcts.csv", index=False)