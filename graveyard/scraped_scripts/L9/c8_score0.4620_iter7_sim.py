import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_8/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_8/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df_all = pd.concat(dfs, ignore_index=True)

agg_df = df_all.groupby(['admit', 'prestige'], as_index=False).agg({'gre':'sum', 'gpa':'sum'})

agg_df['admit'] = agg_df['admit'].astype(int)
agg_df['prestige'] = agg_df['prestige'].astype(int)
agg_df['gre'] = agg_df['gre'].astype(int)
agg_df['gpa'] = agg_df['gpa'].astype(float)

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_8/target_multisource_mcts.csv", index=False)