import pandas as pd

source_path = 'autopipeline-benchmarks/github-pipelines/length1_46/test_0.csv'
df = pd.read_csv(source_path, index_col=0)
result = df.groupby('Text Date').agg(
    {'Water Use': 'sum', 'Power Use': 'sum'}
).reset_index()
result.rename(columns={'Text Date': 'Date'}, inplace=True)
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_46/target_multisource_mcts_recovery_test_val.csv', index=False)