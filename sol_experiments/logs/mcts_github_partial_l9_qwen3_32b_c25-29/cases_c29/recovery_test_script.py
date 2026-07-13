import pandas as pd

source0_path = 'autopipeline-benchmarks/github-pipelines/length9_29/test_0.csv'
source0 = pd.read_csv(source0_path, index_col=0)
grouped = source0.groupby('COLLECTION_EVENTS_NUM').first().reset_index()
grouped.to_csv('autopipeline-benchmarks/github-pipelines/length9_29/target_multisource_mcts_recovery_test_val.csv', index=False)