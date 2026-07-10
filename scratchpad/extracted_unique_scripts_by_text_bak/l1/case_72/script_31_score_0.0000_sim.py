import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_72/training_0.csv', index_col=0)
df1 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_72/training_1.csv', index_col=0)
df2 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_72/training_2.csv', index_col=0)

df = pd.concat([df0, df1, df2], ignore_index=True)

pivot_df = df.groupby('condition')['click'].sum().reset_index()

pivot_df.columns = ['condition', '0']
pivot_df['condition'] = pivot_df['condition'].astype(int)
pivot_df['0'] = pivot_df['0'].astype(int)

pivot_df.to_csv('autopipeline-benchmarks/github-pipelines/length1_72/target_multisource_mcts.csv', index=False)