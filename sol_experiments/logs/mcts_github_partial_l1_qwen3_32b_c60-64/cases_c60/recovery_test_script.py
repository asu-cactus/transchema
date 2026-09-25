import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_60/test_0.csv', index_col=0)
aggregated_df = df0.groupby("type", as_index=False).agg({"driver_count": "sum"})
aggregated_df.to_csv('autopipeline-benchmarks/github-pipelines/length1_60/target_multisource_mcts_recovery_test_val.csv', index=False)