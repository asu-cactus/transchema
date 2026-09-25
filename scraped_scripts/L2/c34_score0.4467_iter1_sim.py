import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_34/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_34/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=['city', 'type'], value_vars=['driver_count'], var_name='variable', value_name='ride_id')
df0_unpivot = df0_unpivot[['city', 'ride_id']]

df1_sel = df1[['city', 'ride_id']]

result = pd.concat([df1_sel, df0_unpivot], ignore_index=True)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_34/target_multisource_mcts.csv", index=False)