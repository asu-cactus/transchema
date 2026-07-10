import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_84/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_84/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)

agg_df = union_df.groupby('prestige').agg(
    admit=('admit', 'sum'),
    gre=('gre', 'mean'),
    gpa=('gpa', 'min')
).reset_index()

agg_df['admit'] = agg_df['admit'].astype(int)
agg_df['gre'] = agg_df['gre'].round().astype(int)
agg_df['gpa'] = agg_df['gpa'].astype(float)
agg_df['prestige'] = agg_df['prestige'].astype(int)

agg_df = agg_df[['admit', 'gre', 'gpa', 'prestige']]

agg_df.to_csv("autopipeline-benchmarks/github-pipelines/length9_84/target_multisource_mcts.csv", index=False)