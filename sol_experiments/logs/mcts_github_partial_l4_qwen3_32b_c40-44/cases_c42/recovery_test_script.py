import pandas as pd

dfs = [
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_42/test_0.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_42/test_1.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_42/test_2.csv', index_col=0),
    pd.read_csv('autopipeline-benchmarks/github-pipelines/length4_42/test_3.csv', index_col=0)
]

df = pd.concat(dfs, ignore_index=True)
result = df.groupby('location', as_index=False).agg(
    title=('title', 'nunique'),
    company=('company', 'nunique'),
    summary=('summary', 'nunique'),
    salary=('salary', 'nunique'),
    href=('href', 'nunique'),
    rate=('rate', 'nunique'),
    reviews=('reviews', 'nunique'),
    org_salary_period=('org_salary_period', 'nunique')
)
result.to_csv('autopipeline-benchmarks/github-pipelines/length4_42/target_multisource_mcts_recovery_test_val.csv', index=False)