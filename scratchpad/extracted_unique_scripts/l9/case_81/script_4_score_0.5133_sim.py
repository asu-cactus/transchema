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

grouped = union_df.groupby(['admit', 'prestige'], as_index=False).agg(
    admit_count=('admit', 'count'),
    gre_avg=('gre', 'mean'),
    gpa_avg=('gpa', 'mean')
)

result = grouped.rename(columns={
    'admit': 'admit',
    'prestige': 'prestige',
    'gre_avg': 'gre',
    'gpa_avg': 'gpa'
})

result['admit'] = result['admit'].astype(int)
result['prestige'] = result['prestige'].astype(int)
result['gre'] = result['gre'].round().astype(int)
result['gpa'] = result['gpa'].astype(float)

result = result[['admit', 'gre', 'gpa', 'prestige']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_81/target_multisource_mcts.csv", index=False)