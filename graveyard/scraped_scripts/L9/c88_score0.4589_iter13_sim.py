import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length9_88/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_3.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_4.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_5.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_6.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_7.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_8.csv",
    "autopipeline-benchmarks/github-pipelines/length9_88/training_9.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
union_df = pd.concat(dfs, ignore_index=True)

agg_df = union_df.groupby(['admit', 'prestige'], as_index=False).agg({
    'gre': 'sum',
    'gpa': ['min', 'max']
})

agg_df.columns = ['admit', 'prestige', 'gre', 'gpa_min', 'gpa_max']

agg_df['gpa'] = (agg_df['gpa_min'] + agg_df['gpa_max']) / 2

result = agg_df[['admit', 'gre', 'gpa', 'prestige']]

result['admit'] = result['admit'].astype(int)
result['gre'] = result['gre'].astype(int)
result['prestige'] = result['prestige'].astype(int)
result['gpa'] = result['gpa'].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length9_88/target_multisource_mcts.csv", index=False)