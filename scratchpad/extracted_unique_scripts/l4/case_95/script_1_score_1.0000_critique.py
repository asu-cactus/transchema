import pandas as pd

paths = [
    "autopipeline-benchmarks/github-pipelines/length4_95/training_0.csv",
    "autopipeline-benchmarks/github-pipelines/length4_95/training_1.csv",
    "autopipeline-benchmarks/github-pipelines/length4_95/training_2.csv",
    "autopipeline-benchmarks/github-pipelines/length4_95/training_3.csv"
]

agg_cols = ['PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']

grouped_dfs = []
for p in paths:
    df = pd.read_csv(p, index_col=0)
    # Group by 'Subject', aggregate count and sums
    grouped = df.groupby('Subject', as_index=False).agg(
        SubjectId=('SubjectId', 'count'),
        Split=('SubjectId', 'count'),
        PA=('PA', 'sum'),
        AB=('AB', 'sum'),
        H=('H', 'sum'),
        TB=('TB', 'sum'),
        BB=('BB', 'sum'),
        SF=('SF', 'sum'),
        HBP=('HBP', 'sum')
    )
    grouped_dfs.append(grouped)

# Union all grouped dataframes
result = pd.concat(grouped_dfs, ignore_index=True)

# Ensure correct dtypes
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
})

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_95/target_multisource_mcts.csv", index=False)