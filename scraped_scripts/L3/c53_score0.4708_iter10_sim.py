import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

df_all = pd.concat([df0, df1, df2], ignore_index=True)

agg = df_all.groupby(['ID Number', 'Name', 'Fed', 'Sex'], as_index=False).agg({'B-day': ['min', 'max']})

agg.columns = ['ID Number', 'Name', 'Fed', 'Sex', 'B-day_min', 'B-day_max']

agg['B-day'] = agg['B-day_min']

agg = agg.rename(columns={'Name': 'Name_x', 'Fed': 'Fed_x', 'Sex': 'Sex_x'})

result = agg[['B-day', 'ID Number', 'Name_x', 'Fed_x', 'Sex_x']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)