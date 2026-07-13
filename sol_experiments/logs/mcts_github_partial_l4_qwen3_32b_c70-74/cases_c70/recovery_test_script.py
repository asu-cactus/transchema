import pandas as pd

source_files = [
    'autopipeline-benchmarks/github-pipelines/length4_70/test_0.csv',
    'autopipeline-benchmarks/github-pipelines/length4_70/test_1.csv',
    'autopipeline-benchmarks/github-pipelines/length4_70/test_2.csv',
    'autopipeline-benchmarks/github-pipelines/length4_70/test_3.csv',
    'autopipeline-benchmarks/github-pipelines/length4_70/test_4.csv'
]

dfs = []
for file in source_files:
    df = pd.read_csv(file, index_col=0, dtype={
        'GEO.id': str,
        'GEO.id2': str,
        'GEO.display-label': str,
        'HD01_VD01': str,
        'HD02_VD01': str,
        'Year': int
    })
    dfs.append(df)

pd.concat(dfs, ignore_index=True).to_csv(
    'autopipeline-benchmarks/github-pipelines/length4_70/target_multisource_mcts_recovery_test_val.csv',
    index=False
)