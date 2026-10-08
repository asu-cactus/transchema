import pandas as pd
import numpy as np

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

df0['Passing Math'] = (df0['math_score'] >= 70).astype(int)
df0['Passing Reading'] = (df0['reading_score'] >= 70).astype(int)

agg = df0.groupby('school').agg(
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean'),
    Number_Students=('Student ID', 'count'),
    Number_Passing_Math=('Passing Math', 'sum'),
    Number_Passing_Reading=('Passing Reading', 'sum')
).reset_index()

join1 = pd.merge(agg, df1, left_on='school', right_on='name', how='inner')

final = pd.merge(join1, df2, left_on='name', right_on='school', how='inner', suffixes=('_agg', '_src2'))

# Use columns from df1 for School ID, name, type, size, budget
# Use aggregated columns from agg (Average Math Score, Average Reading Score, Number Passing Math, Number Passing Reading)
# The target schema is:
# ['School ID': int, 'name': str, 'type': str, 'size': int, 'budget': int,
#  'Average Math Score': float, 'Average Reading Score': float,
#  'Number Passing Math': int, 'Number Passing Reading': int]

result = pd.DataFrame()
result['School ID'] = final['School ID'].astype(int)
result['name'] = final['name']
result['type'] = final['type']
result['size'] = final['size'].astype(int)
result['budget'] = final['budget'].astype(int)
result['Average Math Score'] = final['Average_Math_Score'].astype(float)
result['Average Reading Score'] = final['Average_Reading_Score'].astype(float)
result['Number Passing Math'] = final['Number_Passing_Math'].astype(int)
result['Number Passing Reading'] = final['Number_Passing_Reading'].astype(int)

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)