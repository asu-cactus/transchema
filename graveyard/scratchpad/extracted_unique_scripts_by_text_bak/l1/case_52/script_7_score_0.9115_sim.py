import pandas as pd

df = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_52/training_0.csv', index_col=0)
pivot_df = df.groupby('condition')['click'].count().reset_index()
pivot_df = pivot_df.rename(columns={'click': '0'})
pivot_df['condition'] = pivot_df['condition'].astype(int)
pivot_df['0'] = pivot_df['0'].astype(int)
pivot_df.to_csv('autopipeline-benchmarks/github-pipelines/length1_52/target_multisource_mcts.csv', index=False)