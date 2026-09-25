import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

pivot_df = df0.pivot_table(index='city', columns='date', values='fare', aggfunc='mean').reset_index()

agg_df = df0.groupby('city').agg(a=('fare', 'mean')).reset_index()

merged = pd.merge(agg_df, df1[['city', 'driver_count']], on='city', how='inner')

merged = merged.rename(columns={'driver_count': 'b'})

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)