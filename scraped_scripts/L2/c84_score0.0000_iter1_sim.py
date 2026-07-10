import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_84/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_84/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=['city', 'type'], value_vars=['driver_count'], var_name='variable', value_name='ride_id')
df0_unpivot = df0_unpivot.drop(columns=['variable'])

merged = pd.merge(df0_unpivot, df1[['city', 'ride_id']], how='inner', left_on=['type', 'ride_id'], right_on=['city', 'ride_id'])

result = merged[['type', 'ride_id']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_84/target_multisource_mcts.csv", index=False)