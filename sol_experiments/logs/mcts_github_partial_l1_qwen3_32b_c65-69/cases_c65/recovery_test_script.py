import pandas as pd

df = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_65/test_0.csv", index_col=0)
filtered_df = df[df['revenue'] > 0]
result = filtered_df.groupby('year').size().reset_index(name='0')
result.to_csv("autopipeline-benchmarks/github-pipelines/length1_65/target_multisource_mcts_recovery_test_val.csv", index=False)