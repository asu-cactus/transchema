import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length1_98/training_1.csv", index_col=0)

df0_unpivot = df0.melt(id_vars=['right_index'], value_vars=['0'], var_name='variable', value_name='0_x')

df_merged = df0_unpivot.merge(df1, left_on='right_index', right_index=True, how='inner')
df_merged = df_merged.rename(columns={'0': '0_y'})

result = df_merged[['0_x', '0_y']].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length1_98/target_multisource_mcts.csv", index=False)