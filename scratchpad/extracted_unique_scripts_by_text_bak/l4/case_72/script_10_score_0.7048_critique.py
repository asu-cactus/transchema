import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_72/training_1.csv", index_col=0)

agg_df = df0.groupby('city', as_index=False).agg(a=('fare', 'mean'))

merged = pd.merge(agg_df, df1[['city', 'driver_count']], on='city', how='inner')

merged = merged.rename(columns={'driver_count': 'b'})

merged.to_csv("autopipeline-benchmarks/github-pipelines/length4_72/target_multisource_mcts.csv", index=False)