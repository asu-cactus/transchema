import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_11/training_0.csv", index_col=0)
df0 = df0[['SN', 'Price']]
df_agg = df0.groupby(['SN', 'Price'], as_index=False).size().rename(columns={'size': 'count'})
df_agg['SN'] = df_agg['SN'].astype(str)
df_agg['Price'] = df_agg['Price'].astype(float)
df_agg['count'] = df_agg['count'].astype(int)
df_agg.to_csv("autopipeline-benchmarks/github-pipelines/length3_11/target_multisource_mcts.csv", index=False)