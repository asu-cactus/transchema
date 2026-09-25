import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_80/training_0.csv", index_col=0)
df_unpivoted = df0.melt(var_name='variable', value_name='value')
df_pivoted = df_unpivoted.pivot(columns='variable', values='value').reset_index(drop=True)
df_pivoted.columns = df_pivoted.columns.astype(str)
df_pivoted = df_pivoted[['0', '1', '2', '3']]
df_pivoted.to_csv("autopipeline-benchmarks/github-pipelines/length2_80/target_multisource_mcts.csv", index=False)