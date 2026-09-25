import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

df_join = pd.merge(df0, df2, on="ID Number", suffixes=('_x', '_y'))

df_pivot = df_join.pivot(index='B-day_x', columns='ID Number', values=['Name_x', 'Fed_x', 'Sex_x'])

df_pivot.columns = [f"{col[0]}_{col[1]}" for col in df_pivot.columns]
df_pivot = df_pivot.reset_index()

df_pivot = df_pivot.rename(columns={'B-day_x': 'B-day'})

df_pivot = df_pivot.astype({'B-day': 'Int64'})

df_pivot.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)