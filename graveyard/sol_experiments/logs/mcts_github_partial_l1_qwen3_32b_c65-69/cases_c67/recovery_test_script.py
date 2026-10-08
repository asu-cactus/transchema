import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_67/test_0.csv', index_col=0)
result = df.groupby('user_id')[['sad.depressed', 'open.stressed']].mean().rename(columns={'sad.depressed': 'sad', 'open.stressed': 'stressed'}).reset_index()
result.to_csv('autopipeline-benchmarks/github-pipelines/length1_67/target_multisource_mcts_recovery_test_val.csv', index=False)