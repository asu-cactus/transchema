import pandas as pd

df0 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_0.csv", index_col=0)
df1 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_1.csv", index_col=0)
df2 = pd.read_csv("autopipeline-benchmarks/github-pipelines/length4_77/training_2.csv", index_col=0)

agg = df0.groupby(['school']).agg(
    Number_Passing_Math=('math_score', lambda x: (x >= 60).sum()),
    Number_Passing_Reading=('reading_score', lambda x: (x >= 60).sum()),
    Average_Math_Score=('math_score', 'mean'),
    Average_Reading_Score=('reading_score', 'mean'),
    Number_Students=('Student ID', 'count')
).reset_index()

merged1 = pd.merge(df1, agg, left_on='name', right_on='school', how='left')

merged2 = pd.merge(merged1, df2, left_on='name', right_on='school', how='left', suffixes=('', '_src2'))

result = merged2[['School ID', 'name', 'type', 'size', 'budget',
                  'Average_Math_Score', 'Average_Reading_Score',
                  'Number_Passing_Math', 'Number_Passing_Reading']]

result = result.rename(columns={
    'Average_Math_Score': 'Average Math Score',
    'Average_Reading_Score': 'Average Reading Score',
    'Number_Passing_Math': 'Number Passing Math',
    'Number_Passing_Reading': 'Number Passing Reading'
})

result['School ID'] = result['School ID'].astype('Int64')
result['size'] = result['size'].astype('Int64')
result['budget'] = result['budget'].astype('Int64')
result['Number Passing Math'] = result['Number Passing Math'].astype('Int64')
result['Number Passing Reading'] = result['Number Passing Reading'].astype('Int64')

result.to_csv("autopipeline-benchmarks/github-pipelines/length4_77/target_multisource_mcts.csv", index=False)