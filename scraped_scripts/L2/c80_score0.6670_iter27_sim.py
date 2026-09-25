import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length2_80/training_0.csv", index_col=0)

df_joined = pd.merge(df0, df0, left_on='0', right_on='0')

df_unpivot = df_joined.melt(id_vars=['0'], value_vars=['1_x', '2_x', '3_x', '1_y', '2_y', '3_y'], value_name='value')

df_unpivot = df_unpivot.rename(columns={'0': '0', 'variable': '1'})

df_unpivot['1'] = df_unpivot['1'].map({'1_x': 1.0, '2_x': 2.0, '3_x': 3.0, '1_y': 1.0, '2_y': 2.0, '3_y': 3.0})

df_unpivot['2'] = 0.0

df_unpivot['3'] = df_unpivot['value']

result = df_unpivot[['0', '1', '2', '3']].astype(float)

result.to_csv("autopipeline-benchmarks/github-pipelines/length2_80/target_multisource_mcts.csv", index=False)