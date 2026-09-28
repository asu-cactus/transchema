import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_95/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_95/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_95/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_95/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]

df = pd.concat(dfs, ignore_index=True)

agg_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']
group_cols = ['Subject', 'SubjectId', 'Split']

result = df.groupby(group_cols, as_index=False)[agg_cols].sum()

result = result.astype({
    'Subject': str,
    'SubjectId': 'int64',
    'Split': 'int64',
    'PA': 'int64',
    'AB': 'int64',
    'H': 'int64',
    'TB': 'int64',
    'BB': 'int64',
    'SF': 'int64',
    'HBP': 'int64'
}, errors='ignore')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_95/target_multisource_mcts.csv", index=False)