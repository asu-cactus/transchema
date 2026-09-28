import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_41/test_0.csv', index_col=0)
result = df.groupby('zipcode', as_index=False).agg({
    'AGI_STUB': 'first',
    'N1': 'sum',
    'A00100': 'sum'
}).astype({
    'zipcode': int,
    'AGI_STUB': int,
    'N1': int,
    'A00100': int
})

result.to_csv('autopipeline-benchmarks/github-pipelines/length1_41/target_multisource_mcts_recovery_test_val.csv', index=False)