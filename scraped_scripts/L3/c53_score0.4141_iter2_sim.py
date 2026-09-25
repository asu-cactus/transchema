import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length3_53/training_2.csv", index_col=0)

agg0 = df0.groupby(['ID Number', 'Name', 'Fed', 'Sex'], dropna=False).agg(
    COUNT_ID_Number=('ID Number', 'count'),
    AVG_B_day=('B-day', 'mean')
).reset_index()

agg1 = df1.groupby(['ID Number', 'Name', 'Fed', 'Sex'], dropna=False).agg(
    COUNT_ID_Number=('ID Number', 'count'),
    AVG_B_day=('B-day', 'mean')
).reset_index()

agg2 = df2.groupby(['ID Number', 'Name', 'Fed', 'Sex'], dropna=False).agg(
    COUNT_ID_Number=('ID Number', 'count'),
    AVG_B_day=('B-day', 'mean')
).reset_index()

union_df = pd.concat([agg0, agg1, agg2], ignore_index=True)

final_agg = union_df.groupby(['ID Number', 'Name', 'Fed', 'Sex'], dropna=False).agg(
    ID_Number=('COUNT_ID_Number', 'sum'),
    B_day=('AVG_B_day', 'mean')
).reset_index()

final_agg['B-day'] = final_agg['B_day'].round().astype('Int64')
final_agg['ID Number'] = final_agg['ID_Number'].astype('Int64')
final_agg['Name_x'] = final_agg['ID Number']
final_agg['Fed_x'] = final_agg['ID Number']
final_agg['Sex_x'] = final_agg['ID Number']

result = final_agg[['B-day', 'ID Number', 'Name_x', 'Fed_x', 'Sex_x']]

result.to_csv("autopipeline-benchmarks/github-pipelines/length3_53/target_multisource_mcts.csv", index=False)