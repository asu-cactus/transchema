import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_82/test_0.csv', index_col=0)
result = df.dropna(subset=['conservation_status']).groupby('conservation_status', as_index=False).agg(scientific_name=('scientific_name', 'count'))
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_82/target_multisource_mcts_recovery_test_val.csv', index=False)