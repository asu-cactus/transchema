import pandas as pd

df0 = pd.read_csv('autopipeline-benchmarks/github-pipelines/length1_95/training_0.csv', index_col=0, parse_dates=['date'])

df_grouped = df0.groupby('customer_id', as_index=False)['date'].max()

df_grouped['date'] = df_grouped['date'].dt.strftime('%Y-%m-%d')

df_grouped.to_csv('autopipeline-benchmarks/github-pipelines/length1_95/target_multisource_mcts.csv', index=False)