import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_75/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_75/training_1.csv", index_col=0)

pivot_result = df0.pivot_table(index='city', columns='date', values='fare', aggfunc='mean').reset_index()

joined = pd.merge(pivot_result, df1, on='city', how='inner')

melted = joined.melt(id_vars=['city', 'type'], value_name='fare', var_name='date')

result = melted.groupby(['city', 'type'], as_index=False)['fare'].mean()

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_75/target_multisource_mcts.csv", index=False)