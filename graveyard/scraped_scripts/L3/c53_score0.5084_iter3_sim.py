import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

df_join = pd.merge(df0, df2, on="ID Number", suffixes=('_x', '_y'))

df_result = df_join.groupby(['B-day_x', 'ID Number', 'Name_x', 'Fed_x', 'Sex_x'], as_index=False).size()

df_result = df_result.rename(columns={'B-day_x': 'B-day'})

df_result = df_result[['B-day', 'ID Number', 'Name_x', 'Fed_x', 'Sex_x']]

df_result.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)