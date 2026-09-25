import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_70/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_70/training_1.csv", index_col=0)

pivot_result = df0.pivot(index='city', columns='date', values='fare').reset_index()

join_result = pivot_result.merge(df1[['city', 'type']], on='city', how='inner')

date_cols = [col for col in join_result.columns if col not in ['city', 'type']]

melt_result = join_result.melt(id_vars=['city', 'type'], value_vars=date_cols, var_name='date', value_name='fare')

final_df = melt_result[['city', 'type', 'fare']]

final_df.to_csv("autopipeline-benchmarks/github-pipelines/length3_70/target_multisource_mcts.csv", index=False)