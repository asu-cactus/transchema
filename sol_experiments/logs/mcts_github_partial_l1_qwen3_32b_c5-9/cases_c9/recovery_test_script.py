import pandas as pd

source_path = 'autopipeline-benchmarks/github-pipelines/length1_9/test_0.csv'
df = pd.read_csv(source_path, index_col=0)
result = df.groupby('zipcode', as_index=False).agg({
    'AGI_STUB': 'first',
    'N1': 'sum',
    'A00100': 'sum'
})
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_9/target_multisource_mcts_recovery_test_val.csv', index=False)