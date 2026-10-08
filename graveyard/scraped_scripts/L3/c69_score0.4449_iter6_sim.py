import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_69/training_1.csv", index_col=0)

joined = pd.merge(df0, df1[['city', 'fare']], on='city')

grouped = joined.groupby(['city', 'type'], as_index=False)['fare'].mean()

pivoted = grouped.pivot(index='city', columns='type', values='fare').reset_index()

melted = pivoted.melt(id_vars='city', var_name='type', value_name='fare')

melted['city'] = melted['city'].astype(str)
melted['type'] = melted['type'].astype(str)
melted['fare'] = melted['fare'].astype(float)

melted.to_csv("autopipeline-benchmarks/github-pipelines/length3_69/target_multisource_mcts.csv", index=False)