import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

join_01 = pd.merge(df0, df1, on="ID Number", suffixes=('_x', '_y'))
final_join = pd.merge(join_01, df2, on="ID Number", suffixes=('', '_z'))

result = final_join[['B-day_x', 'ID Number', 'Name_x', 'Fed_x', 'Sex_x']].copy()
result.rename(columns={'B-day_x': 'B-day'}, inplace=True)

result['B-day'] = pd.to_numeric(result['B-day'], errors='coerce').astype('Int64')
result['ID Number'] = pd.to_numeric(result['ID Number'], errors='coerce').astype('Int64')
result['Name_x'] = pd.to_numeric(result['Name_x'], errors='coerce').astype('Int64')
result['Fed_x'] = pd.to_numeric(result['Fed_x'], errors='coerce').astype('Int64')
result['Sex_x'] = pd.to_numeric(result['Sex_x'], errors='coerce').astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)