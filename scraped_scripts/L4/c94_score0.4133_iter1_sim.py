import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_94/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_94/training_3.csv"
]

dfs = [pd.read_csv(p, index_col=0) for p in paths]
df = pd.concat(dfs, ignore_index=True)

df = df.astype({
    'Split': str,
    'SubjectId': 'Int64',
    'Subject': 'Int64',
    'PA': 'Int64',
    'AB': 'Int64',
    'H': 'Int64',
    'TB': 'Int64',
    'BB': 'Int64',
    'SF': 'Int64',
    'HBP': 'Int64'
}, errors='ignore')

df.to_csv("autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts.csv", index=False)