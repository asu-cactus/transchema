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
union_df = pd.concat(dfs, ignore_index=True)

agg_df = union_df.groupby(['admit', 'prestige']).agg(
    admit_count=('admit', 'count'),
    gre_avg=('gre', 'mean'),
    gpa_min=('gpa', 'min'),
    gpa_max=('gpa', 'max')
).reset_index()

agg_df['gre'] = agg_df['gre_avg'].round().astype(int)
agg_df['gpa'] = ((agg_df['gpa_min'] + agg_df['gpa_max']) / 2).astype(float)
agg_df['admit'] = agg_df['admit'].astype(int)
agg_df['prestige'] = agg_df['prestige'].astype(int)

result = agg_df[['admit', 'gre', 'gpa', 'prestige']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_82/target_multisource_mcts.csv", index=False)