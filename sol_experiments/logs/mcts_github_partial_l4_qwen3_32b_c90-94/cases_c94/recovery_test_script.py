import pandas as pd

dfs = []
sources = [
    'autopipeline-benchmarks/github-pipelines/length4_94/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_94/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_94/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_94/test_3.csv'
]

for source in sources:
    df = pd.read_csv(source, index_col=0)
    df['Subject'] = df['SubjectId'].astype(int)
    dfs.append(df[['Split', 'SubjectId', 'Subject', 'PA', 'AB', 'H', 'TB', 'BB', 'SF', 'HBP']])

result = pd.concat(dfs).drop_duplicates()
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_94/target_multisource_mcts_recovery_test_val.csv', index=False)