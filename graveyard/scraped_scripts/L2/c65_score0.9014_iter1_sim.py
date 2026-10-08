import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_65/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_65/training_1.csv", index_col=0)

df1_unpivot = df1.melt(id_vars=['fname'], value_vars=[col for col in df1.columns if col != 'fname'], var_name='variable', value_name='value')
df1_unpivot = df1_unpivot[['fname']]

df0_subset = df0[['fname']]

combined = pd.concat([df0_subset, df1_unpivot], ignore_index=True)

result = combined.groupby('fname').size().reset_index(name='row_count')

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_65/target_multisource_mcts.csv", index=False)