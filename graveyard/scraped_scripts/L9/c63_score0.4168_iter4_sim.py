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

agg = df_all.groupby(['admit', 'prestige']).agg(
    admit_count=('admit', 'count'),
    gre_avg=('gre', 'mean'),
    gpa_avg=('gpa', 'mean')
).reset_index()

agg['admit'] = agg['admit_count'].astype(int)
agg['gre'] = agg['gre_avg'].round().astype(int)
agg['gpa'] = agg['gpa_avg'].astype(float)
agg['prestige'] = agg['prestige'].astype(int)

result = agg[['admit', 'gre', 'gpa', 'prestige']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_63/target_multisource_mcts.csv", index=False)